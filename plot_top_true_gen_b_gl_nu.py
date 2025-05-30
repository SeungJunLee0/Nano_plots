#!/usr/bin/env python
import ROOT

# 1) 파일 열기
f = ROOT.TFile.Open("merge.root")
if not f or f.IsZombie():
    raise RuntimeError("merge.root 파일을 열 수 없습니다")

# 2) plots 디렉토리 가져오기
plots = f.Get("plots")
if not plots:
    raise RuntimeError("'plots' 디렉토리를 찾을 수 없습니다")

# 3) 히스토그램 가져오기
h_top  = plots.Get("topmass")       # merge.root 안의 hist 이름
h_true = plots.Get("gen_b_gl_nu")   # merge.root 안의 hist 이름

if not h_top or not h_true:
    # 키가 뭔지 찍어보고
    print("plots 디렉토리의 contents:")
    plots.ls()
    raise RuntimeError("히스토그램 이름을 확인해주세요")

# 4) 스타일 설정
# → 4.1) 노말라이제이션: 면적을 1로 맞춰준다
if h_top.Integral() > 0:
    h_top.Scale(1.0 / h_top.Integral())
if h_true.Integral() > 0:
    h_true.Scale(1.0 / h_true.Integral())
h_top.SetLineColor(ROOT.kRed)
h_top.SetLineWidth(2)
h_true.SetLineColor(ROOT.kBlue)
h_true.SetLineWidth(2)

# 5) Canvas 에 그리기
c = ROOT.TCanvas("c_overlay","Top vs True b+ℓ+ν",800,600)
h_top.Draw("HIST")              # 먼저 빨간색 히스토그램
h_true.Draw("HIST SAME")       # 그 위에 파란색

# 6) 범례 추가
leg = ROOT.TLegend(0.6, 0.7, 0.88, 0.88)
leg.AddEntry(h_top,  "Reconstructed top mass",    "l")
leg.AddEntry(h_true, "last b+ℓ+ν invariant mass",  "l")
leg.Draw()

# 7) 결과 저장
c.SaveAs("top_vs_true_overlay.png")
print("overlay 그림을 top_vs_true_overlay.png 로 저장했습니다")

