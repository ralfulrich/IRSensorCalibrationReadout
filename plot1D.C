#include <TGraph.h>
#include <TCanvas.h>
#include <string>

using namespace std;

void plot1D() {

  //string fn = "tmp.dat";
  string fn="pre-scan.dat";
  TGraph* g1 = new TGraph(fn.c_str(), "%*lg %lg %lg");
  TGraph* g2 = new TGraph(fn.c_str(), "%*lg %lg %*lg %lg");
  TGraph* g3 = new TGraph(fn.c_str(), "%*lg %lg %*lg %*lg %lg");

  g1->SetLineColor(kRed);
  g1->SetMarkerColor(kRed);
  g2->SetLineColor(kBlue);
  g2->SetMarkerColor(kBlue);
  g3->SetLineColor(kGreen+1);
  g3->SetMarkerColor(kGreen+1);

  TCanvas* canvas = new TCanvas("canvas1D");
  canvas->SetLogy(1);
  
  g3->Draw("alp");
  g2->Draw("lp");
  g1->Draw("lp");
  
  
}
