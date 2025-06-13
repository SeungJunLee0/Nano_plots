{

// ROOT에서 실행
TFile *f = new TFile("result.root", "UPDATE");  // UPDATE 모드로 열기
f->cd("plots");

// 해당 Canvas 불러오기
TCanvas *c = (TCanvas*)gDirectory->Get("c_b_all_pt_eta");
c->Draw();  // 캔버스 열어보기

// 히스토그램 객체 가져오기
TH2F *h = (TH2F*)c->GetListOfPrimitives()->FindObject("b_all_pt_eta");

// 축 이름 수정
h->GetXaxis()->SetTitle("p_{T} [GeV]");
h->GetYaxis()->SetTitle("#eta");

// 다시 캔버스에 그리기
c->cd();
h->Draw("COLZ");

// 수정 사항 저장
c->Modified();
c->Update();
f->cd("plots");
c->Write("", TObject::kOverwrite);  // 기존 캔버스를 덮어쓰기
f->Close();

}
