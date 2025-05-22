import ROOT
import numpy as np
import matplotlib.pyplot as plt

# 파일 열기
f = ROOT.TFile.Open("merge.root")
plots = f.Get("plots")

# 히스토그램 불러오기
h_meas = plots.Get("topmass")             # measured (reco-level)
h_truth = plots.Get("gen_j_l_nu")            # truth (gen-level)
#h_truth = plots.Get("gen_j_l")            # truth (gen-level)
h_response = plots.Get("topmass_vs_gen_j_l")  # response matrix

# 히스토그램을 numpy 배열로 변환
n_bins_x = h_response.GetNbinsX()
n_bins_y = h_response.GetNbinsY()

measured = np.array([h_meas.GetBinContent(i+1) for i in range(n_bins_x)])
truth = np.array([h_truth.GetBinContent(i+1) for i in range(n_bins_y)])

# ▶️ Histogram normalization (area to 1)
if h_meas.Integral() > 0:
    measured /= h_meas.Integral()
if h_truth.Integral() > 0:
    truth /= h_truth.Integral()

response = np.zeros((n_bins_x, n_bins_y))
for i in range(n_bins_x):
    for j in range(n_bins_y):
        response[i, j] = h_response.GetBinContent(i+1, j+1)

# ▶️ Response matrix column-wise normalization (P(meas | truth))
col_sums = np.sum(response, axis=0)
# avoid division by zero
col_sums[col_sums == 0] = 1.0
response /= col_sums[np.newaxis, :]

# 베이지안 언폴딩 함수 수동 구현
def bayesian_unfold(measured, response, prior=None, n_iter=4):
    response = np.array(response, dtype=float)
    n_meas, n_truth = response.shape

    # 초기 prior 설정
    if prior is None:
        prior = np.ones(n_truth)
    prior = np.array(prior, dtype=float)
    prior /= np.sum(prior)

    # response normalization: P(meas | truth)
    Rnorm = response.sum(axis=0)
    P_meas_given_truth = response / Rnorm[np.newaxis, :]  # shape: (n_meas, n_truth)

    for iteration in range(n_iter):
        # Bayes' theorem: P(truth | meas)
        posterior = np.zeros((n_truth, n_meas))
        for j in range(n_meas):
            denom = np.sum(P_meas_given_truth[j, :] * prior)
            for i in range(n_truth):
                if denom > 0:
                    posterior[i, j] = P_meas_given_truth[j, i] * prior[i] / denom

        # 새 prior 계산: unfolding
        new_prior = np.zeros(n_truth)
        for i in range(n_truth):
            new_prior[i] = np.sum(posterior[i, :] * measured)

        # normalize new prior
        prior = new_prior / np.sum(new_prior)

    return prior  # unfolded result

# 실행
unfolded = bayesian_unfold(measured, response, n_iter=100)
# 시각화
bin_edges = np.array([h_truth.GetBinLowEdge(i+1) for i in range(h_truth.GetNbinsX()+1)])
plt.step(bin_edges[:-1], unfolded, where="post", label="Unfolded", color="red")
plt.step(bin_edges[:-1], truth, where="post", label="True (gen_j_l)", color="black", linestyle="--")
plt.xlabel("mass [GeV]")
plt.ylabel("Normalized Events")
plt.legend()
plt.title("Bayesian Unfolding (Hand-coded, Normalized)")
plt.grid()
plt.savefig("unfold_result.png")
print("📁 언폴딩 결과를 'unfold_result.png'로 저장했습니다.")



# 중심값(mean)과 width(std)의 계산
bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
unfolded_sum = np.sum(unfolded)
mean = np.sum(bin_centers * unfolded) / unfolded_sum
std = np.sqrt(np.sum((bin_centers - mean)**2 * unfolded) / unfolded_sum)

print(f"📊 Unfolded 결과의 평균: {mean:.2f} GeV")
print(f"📏 Unfolded 결과의 width (표준편차): {std:.2f} GeV")




# 1. ROOT histogram으로 변환 (언폴딩 결과 → TH1F)
h_unfolded = ROOT.TH1F("h_unfolded", "Unfolded", len(bin_edges)-1, bin_edges)
for i in range(len(unfolded)):
    h_unfolded.SetBinContent(i+1, unfolded[i])

# 2. Breit-Wigner 함수 정의 (TF1)
bw = ROOT.TF1("bw", "[0] * (0.5*[2])/((x-[1])**2 + 0.25*[2]**2)", bin_edges[0], bin_edges[-1])

# 초기 파라미터: [0]=Norm, [1]=Mean, [2]=Width
initial_norm = h_unfolded.GetMaximum()
initial_mean = h_unfolded.GetBinCenter(h_unfolded.GetMaximumBin())
initial_width = 2.0  # 몇 GeV 가정
initial_mean = 172.5
bw.SetParameters(initial_norm, initial_mean, initial_width)

# 3. 피팅 수행 (R: 범위 제한, S: FitResult 반환)
fit_result = h_unfolded.Fit(bw, "RS")

# 4. 피팅 결과 출력
fit_mean = bw.GetParameter(1)
fit_width = bw.GetParameter(2)
print("📈 Breit-Wigner Fit 결과:")
print(f"   Mean  = {fit_mean:.2f} GeV")
print(f"   Width = {fit_width:.2f} GeV")

# 5. 시각화 (Matplotlib)
bw_x = np.linspace(bin_edges[0], bin_edges[-1], 500)
bw_y = [bw.Eval(x) for x in bw_x]

# 정규화
unfolded_norm = unfolded / np.sum(unfolded)
bw_y_norm = np.array(bw_y) / np.sum(unfolded)

plt.step(bin_centers, unfolded_norm, where="mid", label="Unfolded", color="red")
plt.plot(bw_x, bw_y_norm, 'b--', label="Breit-Wigner Fit")
plt.xlabel("mass [GeV]")
plt.ylabel("Normalized Events")
plt.title("Bayesian Unfolding + Breit-Wigner Fit")
plt.legend()
plt.grid()
plt.savefig("unfold_fit.png")
print("📁 언폴딩 + 피팅 결과를 'unfold_fit.png'로 저장했습니다.")

