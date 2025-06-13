import ROOT
ROOT.gROOT.SetBatch(True)  # ✅ GUI 없이 그림 저장만 하도록 설정

# 입력 및 출력 경로
#input_root = "merge_normalized.root"
input_root = "merge.root"
output_root = "result.root"

# 열기
f_in = ROOT.TFile.Open(input_root)
dir_in = f_in.Get("plots")

# 출력 파일 생성 및 디렉토리
f_out = ROOT.TFile(output_root, "RECREATE")
f_out.mkdir("plots")
f_out.cd("plots")

# 모든 객체 순회
for key in dir_in.GetListOfKeys():
    obj = key.ReadObj()
    name = obj.GetName()

    # 히스토그램만 처리
    if isinstance(obj, (ROOT.TH1, ROOT.TH2, ROOT.TH3)):
        # 캔버스 생성
        canvas = ROOT.TCanvas(f"c_{name}", f"Canvas for {name}", 800, 600)
        obj_clone = obj.Clone()
        obj_clone.SetName(name)

        if isinstance(obj_clone, ROOT.TH1) and not isinstance(obj_clone, ROOT.TH2):
            obj_clone.SetLineColor(ROOT.kBlue)
            obj_clone.SetLineWidth(2)
            obj_clone.SetMarkerStyle(1)
            obj_clone.SetDrawOption("HIST")
            obj_clone.Draw("HIST")
        elif isinstance(obj_clone, ROOT.TH2):
            obj_clone.SetMinimum(0)
            obj_clone.Draw("COLZ")

        canvas.Write()  # canvas를 plots 디렉토리에 저장
        del canvas  # 메모리 정리

f_out.Close()
f_in.Close()
print(f"✅ All histograms drawn and saved as canvases to '{output_root}' under 'plots'.")

