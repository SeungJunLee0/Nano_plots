#!/usr/bin/env python
import ROOT

# 1) 파일 열기
f = ROOT.TFile.Open("merge.root")
if not f or f.IsZombie():
    raise RuntimeError("merge.root 파일을 열 수 없습니다")

# 2) plots 디렉토리에서 TH2F 가져오기
#    key가 "plots/topmass_vs_gen_j_l_nu" 일 수도 있고,
#    디렉토리를 먼저 얻어서 Get() 해도 됩니다.
plots = f.Get("plots")
h2   = plots.Get("topmass_vs_gen_j_l_nu")
if not h2:
    raise RuntimeError("topmass_vs_gen_j_l_nu 히스토그램을 찾을 수 없습니다")

# 3) 축 범위(range) 설정
h2.GetXaxis().SetRangeUser(160, 180)  # x축 160 ~ 180
h2.GetYaxis().SetRangeUser(120, 200)  # y축 120 ~ 200

# 4) (옵션) 최소값 0 으로 설정해서 빈 영역 검정으로
h2.SetMinimum(0)

# 5) 그리기
c = ROOT.TCanvas("c_zoom","topmass_vs_gen_j_l_nu zoom",800,600)
h2.Draw("COLZ")  # COLZ 옵션으로 컬러맵

# 6) 저장
c.SaveAs("topmass_vs_jlnu_zoom.png")
print("zoom 된 그림을 topmass_vs_jlnu_zoom.png 로 저장했습니다")

