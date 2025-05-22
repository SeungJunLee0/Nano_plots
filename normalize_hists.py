import ROOT


input_file = ROOT.TFile.Open("merge.root")
output_file = ROOT.TFile("merge_normalized.root", "RECREATE")
input_dir = input_file.Get("plots")

output_file.mkdir("plots")
output_file.cd("plots")

def normalize_by_x(hist2d):
    nbins_x = hist2d.GetNbinsX()
    nbins_y = hist2d.GetNbinsY()
    normalized = hist2d.Clone(hist2d.GetName() + "_normX")
    normalized.Reset()
    normalized.Sumw2()

    for x in range(1, nbins_x + 1):
        total = sum(hist2d.GetBinContent(x, y) for y in range(1, nbins_y + 1))
        if total == 0:
            continue
        for y in range(1, nbins_y + 1):
            content = hist2d.GetBinContent(x, y) / total
            normalized.SetBinContent(x, y, content)

    return normalized


def normalize_by_y(hist2d):
    nbins_x = hist2d.GetNbinsX()
    nbins_y = hist2d.GetNbinsY()
    normalized = hist2d.Clone(hist2d.GetName() + "_normY")
    normalized.Reset()
    normalized.Sumw2()

    for y in range(1, nbins_y + 1):
        total = sum(hist2d.GetBinContent(x, y) for x in range(1, nbins_x + 1))
        if total == 0: continue
        for x in range(1, nbins_x + 1):
            content = hist2d.GetBinContent(x, y) / total
            normalized.SetBinContent(x, y, content)
    return normalized

# 정규화 대상 리스트
targets = [
    "topmass_vs_true_gen_b_gl_nu",
    "topmass_vs_last_gen_b_gl_nu",
    "last_gen_b_gl_nu_vs_gen_j_l_nu",
    "last_gen_w_mass_vs_reco_w_mass",
    "last_gen_muon_pt_vs_reco_muon_pt",
    "last_gen_muon_eta_vs_reco_muon_eta",
    "last_gen_muon_phi_vs_reco_muon_phi",
    "last_gen_b_pt_vs_reco_j_pt",
    "last_gen_b_eta_vs_reco_j_eta",
    "last_gen_b_phi_vs_reco_j_phi",
    "no_gluon_topmass_vs_true_b_gl_nu_mass",
    "gluon_topmass_vs_true_b_gl_nu_mass",
    "onshellWno_gluon_topmass_vs_true_b_gl_nu_mass",
    "offshellWno_gluon_topmass_vs_true_b_gl_nu_mass",
    "onshellWgluon_topmass_vs_true_b_gl_nu_mass",
    "offshellWgluon_topmass_vs_true_b_gl_nu_mass",
    "noboost_top_onshellW_nogluon_topmass_vs_true_b_gl_nu_mass",
    "boost_top_onshellW_nogluon_topmass_vs_true_b_gl_nu_mass",
    "lowboostW_topmass_vs_true_b_gl_nu_mass",
    "highboostW_topmass_vs_true_b_gl_nu_mass",
    "topmass_vs_true_b_W_mass",
    "angle_vs_mbllnu",
    "true_w_boson_vs_true_l_nu",
    "last_w_boson_vs_true_l_nu"
]
axis_choice = input("정규화할 축을 선택하세요 (x/y): ").strip().lower()
if axis_choice not in ['x', 'y']:
    print("❌ 잘못된 입력입니다. 'x' 또는 'y'를 입력하세요.")
    exit(1)

for key in targets:
    h = input_dir.Get(key)
    if h and isinstance(h, ROOT.TH2F):
        if axis_choice == "y":
            norm = normalize_by_y(h)
        if axis_choice == "x":
            norm = normalize_by_x(h)
        norm.SetEntries(h.GetEntries())  # ✅ 원래 entries 수 복원
        norm.Write()

output_file.Close()
input_file.Close()

