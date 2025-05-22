import ROOT
import numpy as np
import matplotlib.pyplot as plt

# 파일 열기
f = ROOT.TFile.Open("merge.root")
plots = f.Get("plots")

# 히스토그램 불러오기
h_meas = plots.Get("topmass")             # measured (reco-level)
h_truth = plots.Get("gen_j_l")            # truth (gen-level)
h_response = plots.Get("topmass_vs_gen_j_l")  # response matrix

# 히스토그램을 numpy 배열로 변환
n_bins_x = h_response.GetNbinsX()
n_bins_y = h_response.GetNbinsY()

measured = np.array([h_meas.GetBinContent(i+1) for i in range(n_bins_x)])
truth = np.array([h_truth.GetBinContent(i+1) for i in range(n_bins_y)])
response = np.zeros((n_bins_x, n_bins_y))

for i in range(n_bins_x):
    for j in range(n_bins_y):
        response[i, j] = h_response.GetBinContent(i+1, j+1)


# 베이지안 언폴딩 함수 수동 구현
def bayesian_unfold(measured, response, prior=None):
    response = np.array(response, dtype=float)
    n_meas, n_truth = response.shape

    # 초기 prior 설정 (flat or 지정)
    if prior is None:
        prior = np.ones(n_truth)
    prior = np.array(prior, dtype=float)
    prior /= np.sum(prior)

    # normalize response matrix rows to sum to 1 (for each true bin)
    Rnorm = response.sum(axis=0)
    P_meas_given_truth = response / Rnorm[np.newaxis, :]

    # Apply Bayes' theorem: P(true|meas) ∝ P(meas|true) * prior
    posterior = np.zeros((n_truth, n_meas))
    for j in range(n_meas):
        denom = np.sum(P_meas_given_truth[j, :] * prior)
        for i in range(n_truth):
            if denom > 0:
                posterior[i, j] = P_meas_given_truth[j, i] * prior[i] / denom

    # Unfolding: apply posterior to measured
    unfolded = np.zeros(n_truth)
    for i in range(n_truth):
        unfolded[i] = np.sum(posterior[i, :] * measured)

    return unfolded


# 실행
unfolded = bayesian_unfold(measured, response)

# 시각화
bin_edges = np.array([h_truth.GetBinLowEdge(i+1) for i in range(h_truth.GetNbinsX()+1)])
plt.step(bin_edges[:-1], unfolded, where="post", label="Unfolded", color="red")
plt.step(bin_edges[:-1], truth, where="post", label="True (gen_j_l)", color="black", linestyle="--")
plt.xlabel("mass [GeV]")
plt.ylabel("Events")
plt.legend()
plt.title("Bayesian Unfolding (Hand-coded)")
plt.grid()
plt.savefig("unfold_result.png")
print("📁 언폴딩 결과를 'unfold_result.png'로 저장했습니다.")

