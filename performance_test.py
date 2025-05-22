#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to perform unfolding with TUnfold on the gen_j_l vs top_mass response
and fit the unfolded top mass distribution with a Breit-Wigner.

Assumptions:
- The input ROOT file 'merge.root' has a directory 'plots' containing:
    * A TH2 response matrix named 'response_matrix'
    * A TH1 measured distribution named 'gen_j_l'
    * A TH1 truth distribution named 'top_mass' for comparison
- ROOT with TUnfold is available (libUnfold loaded)
"""
import ROOT
import sys

def main():
    # Load the unfolding library
    try:
        ROOT.gSystem.Load("libUnfold")
    except Exception as e:
        print("Failed to load libUnfold:", e)
        sys.exit(1)

    # Open the input file
    fin = ROOT.TFile.Open("merge.root")
    if not fin or fin.IsZombie():
        print("Error: cannot open merge.root")
        sys.exit(1)

    # Retrieve histograms
    h_response = fin.Get("plots/topmass_vs_gen_j_l")
    h_measured = fin.Get("plots/gen_j_l")
    h_truth    = fin.Get("plots/topmass")
    for h, name in [(h_response, "response_matrix"), (h_measured, "gen_j_l"), (h_truth, "top_mass")]:
        if not h:
            print(f"Error: histogram '{name}' not found in 'plots' directory.")
            sys.exit(1)

    # Prepare output histogram (clone truth binning)
    h_unfolded = h_truth.Clone("h_unfolded")
    h_unfolded.Reset()
    h_unfolded.SetTitle("Unfolded Top Mass Distribution")
    h_unfolded.GetXaxis().SetTitle("m_{top} [GeV]")
    h_unfolded.GetYaxis().SetTitle("Events")

    # Initialize TUnfold (output histogram on X-axis)
    unfold = ROOT.TUnfold(
        h_response,
        ROOT.TUnfold.kHistMapOutputHoriz,
        ROOT.TUnfold.kRegModeCurvature
    )

    # L-curve scan to find optimal regularization parameter
    scan = unfold.ScanLcurve(0.0, 0.0, 100, 200)
    # Find tau at maximum curvature
    n = scan.GetN()
    xs = scan.GetX()
    ys = scan.GetY()
    # Find index of max y
    idx_max = max(range(n), key=lambda i: ys[i])
    tau_opt = xs[idx_max]
    print(f"Optimal tau: {tau_opt:.3e}")

    # Perform the unfolding with the chosen tau
    unfold.DoUnfold(tau_opt)
    unfold.GetOutput(h_unfolded)

    # Save unfolded result
    fout = ROOT.TFile("unfolded_result.root", "RECREATE")
    h_unfolded.Write()
    fout.Close()
    print("Unfolded histogram saved to 'unfolded_result.root'.")

    # Breit-Wigner fit on the unfolded distribution
    # Define a Breit-Wigner PDF: N * (0.5*Gamma) / [pi * ((x - M)^2 + (Gamma^2/4))]
    bw_func = ROOT.TF1(
        "bw_func", 
        "[0]*(0.5*[2])/(TMath::Pi()*((x-[1])*(x-[1]) + 0.25*[2]*[2])))", 
        h_unfolded.GetXaxis().GetXmin(), 
        h_unfolded.GetXaxis().GetXmax()
    )
    # Initial parameters: [0]=norm, [1]=mass, [2]=width
    bw_func.SetParameters(h_unfolded.Integral(), 172.5, 2.0)
    bw_func.SetParNames("N","m_{0}","\Gamma")

    # Fit
    fit_res = h_unfolded.Fit(bw_func, "RS")  # R=range, S=return fit result
    mean = bw_func.GetParameter(1)
    width = bw_func.GetParameter(2)
    print(f"Breit-Wigner fit results: mean = {mean:.2f} GeV, width = {width:.2f} GeV")

    # Draw and save the fit result
    canvas = ROOT.TCanvas("c1", "Breit-Wigner Fit", 800, 600)
    h_unfolded.Draw("E")
    bw_func.Draw("Same")
    canvas.SaveAs("breit_wigner_fit.png")
    print("Fit plot saved as 'breit_wigner_fit.png'.")

if __name__ == "__main__":
    main()

