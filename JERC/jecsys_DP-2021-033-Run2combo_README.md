# TrueREADME — what is actually in `jecsys` and what goes where

This file complements `README.md`. It was written after trying to run every
workflow the README mentions, on 2026-10-28, from this exact checkout:

| Item | Value |
|---|---|
| Checkout | detached HEAD at tag `DP-2021-033-Run2combo` (commit `d59d5f5`) |
| Upstream | https://github.com/miquork/jecsys.git |
| Machine | macOS 24.6 (x86_64), Homebrew ROOT **6.32.06**, no CMSSW, no PyROOT |
| Missing inputs | listed in `MissedME.md` |

**Short version of what works here:**

| Workflow (README name) | Driver | Status in this run |
|---|---|---|
| USER: draw one uncertainty source | `test/mk_drawUncertainty.C` | works (path fix on the command line needed, see §3.1) |
| USER: draw source correlations | `test/mk_drawSourceCorrelations.C` | works (same path fix) |
| USER: draw CMS response vs eta | `test/mk_drawCMSresponse.C` | **input missing** (`../JERCProtoLab/...`) |
| (extra) draw ATLAS-style response | `test/mk_drawATLASresponse.C` | **input missing** (`Winter14_V5_MC_*`) |
| (extra) compare JEC versions | `test/mk_compareJECversions.C` | **input missing** (`UL2017_*_MC_*`) |
| EXPERT: derive UncertaintySources | `mk_drawJetCorrectionUncertainty.C` | **works end to end** (105 pdfs + 2 txt files) |
| EXPERT: global fit (L3Res) | `mk_reprocess.C` | **blocked**: raw input missing, 2 compile errors (fixed here), and the archived `jecdataRun2Test.root` is unreadable with ROOT ≥ 6.32 |
| EXPERT: test UncertaintySources | `mk_testSources.C` | **blocked**: macro does not compile under ROOT 6 and its input txt files are not in the repo |

---

## 1. Directory map (what goes where)

```
jecsys/
├── README.md, TrueREADME.md, MissedME.md
├── CondFormats/JetMETObjects/           # standalone copy of the CMSSW JEC classes
│   ├── interface/*.h                    #   FactorizedJetCorrector, JetCorrectorParameters,
│   ├── src/*.cc                         #   JetCorrectionUncertainty, SimpleJetCorrector, ...
│   └── data/*.txt  (1115 files)         #   JEC text files: L1FastJet/L2Relative/L3Absolute/
│                                        #   L2L3Residual/Uncertainty/UncertaintySources per era
├── JetMETCorrections/Modules/           # standalone JetResolution (JER SF) classes
├── test/                                # USER-level drawing macros (see §3)
├── minitools/                           # ~80 one-off study macros (see §6)
├── rootfiles/  (1.9 GB, 320 entries)    # ROOT inputs/outputs of the global fit (see §2.2)
│   ├── jecdata<epoch>.root              #   merged per-epoch inputs produced by reprocess.C
│   ├── flavor/                          #   per-flavour L2Relative txt files used by Flavor.C
│   └── <many group inputs>              #   gamma+jet, Z+jet, multijet, dijet, hadW inputs
├── txt/                                 # UncertaintySources output of the EXPERT chain
│                                        #   (*.txt gitignored except the 2 Summer16 V7 files)
├── textFiles/                           # L2L3Residual txt outputs (UL17 V2/V2M3 archived)
├── pdf/                                 # all plots (*.pdf gitignored); *.tex slide templates
├── mk_*.C                               # DRIVERS: load libraries with ACLiC, then call a macro
├── *.C / *.cpp / *.h                    # the macros themselves (see §2, §4, §5)
└── tdrstyle_mod*.C, tools.C/h, settings.h, globalFitSettings.h   # shared helpers
```

Conventions that are not written down anywhere else:

* **Always run from the repository root** (`jecsys/`). Every `.L CondFormats/...`
  and every `rootfiles/...` path is relative to it. The `test/` drivers are the
  exception and are internally inconsistent (§3.1).
* `mk_*.C` files are *unnamed* ROOT macros (`{ ... }`). They compile the macro
  they need with ACLiC (`.L foo.C+` or `+g`) and then call its entry function.
  ACLiC drops `*_C.so`, `*_C.d`, `*_ACLiC_dict_rdict.pcm` next to the sources;
  all are gitignored.
* Outputs: plots go to `pdf/` (flat for uncertainties, `pdf/<epoch>/` for the
  global fit), text files to `txt/` and `textFiles/`, ROOT outputs back into
  `rootfiles/jecdata<epoch>.root` (opened in `UPDATE` mode).
* `epoch` strings used throughout: `2016BCD, 2016EF, 2016BCDEF, 2016GH,
  2017B..F, 2017BCDEF, 2017H (low PU), 2018A..D, 2018ABCD, Run2Test`.
  `Run2Test` is the Run-2 combination used for DP-2021/033 and is the default
  in `mk_reprocess.C`.

---

## 2. EXPERT workflow A — L3Res global fit (`mk_reprocess.C`)

### 2.1 Data flow

```
 group inputs (rootfiles/*.root, ../JERCProtoLab/...)        [per epoch]
        │
        ▼  reprocess.C : reprocess(epoch)
 rootfiles/jecdata<epoch>.root
   ├── data/eta00-13, data/eta00-25     TH1D/TGraphErrors per channel & alpha cut
   ├── mc/eta00-13,   mc/eta00-25       e.g. mpfchs1_gamjet_a100, ptchs_zjet_a30,
   └── ratio/eta00-13, ratio/eta00-25   chf_/nef_/nhf_ composition, counts_*, mpf1_/mpfn_/mpfu_
        │
        ▼  softrad3.C : softrad3(etamin, etamax, dodraw, epoch)   (HDM 3-point FSR)
   adds  */eta*/fsr/   (hkfsr3_* corrections)
        │
        ▼  globalFitSyst.C : globalFitSyst(epoch)
   adds  */eta*/sys/   (multijet JER, photon scale, hadW fitProb/FSR, incjet HDM, ...)
        │
        ▼  globalFitRenormPF.C : globalFitRenormPF(epoch)
   renormalises CHF+NEF+NHF = 1 for data and MC
        │
        ▼  globalFitL3Res.C : globalFitL3Res(etamin, etamax, epoch, datasets, methods)
   pdf/<epoch>/globalFitL3res_{raw,orig,shifted,doublyshifted,pfjet,kfsr,hsrc}*.pdf
   rootfiles/globalFitL3Res_emat_<epoch>.root       (error matrix)
   textFiles/globalFitL3Res.txt                     (appended fit summary)
   rootfiles/jecdata<epoch>.root  (jesFit + eigenvectors stored when storeJesFit)
```

For `Run2Test` specifically, `reprocess.C` does **not** read the group files;
it reads a single pre-combined file `rootfiles/jecdataRun2TestData.root`
that is produced by `recombine.C` from
`rootfiles/jecdata{2016BCDEF,2016GH,2017BCDEF,2018ABCD}.root` (luminosity
weighted). Only `jecdata2018ABCD.root` of those four is in the repo.

### 2.2 What the `rootfiles/` sub-directories are

| Path | Role |
|---|---|
| `jecdata{A,B,C,D,ABC,ABCD,2018ABCD}.root` | 2018 (Autumn18) merged inputs |
| `jecdata{BCD,EF,GH,BCDEFGH,BCDEF,BCDEF_V4,E,F}.root` | 2016/2017 legacy merged inputs |
| `jecdataRun2Test.root` | the archived Run-2 combination (output of the full chain, written with ROOT 6.18.04) |
| `Gjet_*`, `gamjet_JEC_*` | gamma+jet combination files (EGM) |
| `FullCombination_Z{ee,mm}_*`, `*Zmm*`, `*Zee*` | Z+jet combination files |
| `multijet_*/`, `Autumn18_V1?_L1L2*/` | multijet and dijet L2Res closure inputs |
| `L2Res_*`, `JEC_L2_Dijet_*` | dijet L2Res inputs |
| `Hadrons_1718*.root`, `hadW*.root` | hadronic W / PF hadron studies |
| `flavor/` | Pythia8/Herwig7 per-flavour L2Relative txt used by `Flavor.C` |
| `drawDeltaJEC_*.root` | inclusive-jet "deltaJEC" reference curves |
| `Ratio_Theory/` | NLO theory ratio used by inclusive-jet plots |

### 2.3 How it was run here and what happened

```bash
root -l -b -q mk_reprocess.C
```

1. `gSystem->Load(.../jec-fit-prototype/lib/libjecfit)` fails: that symlink is
   not in the repo. Non-fatal.
2. `tools.C` fails to compile: `tools.h` declared `diffGraphs(g1,g2)` but
   `tools.C` defines `diffGraphs(g1,g2,c1,c2)`. **Fixed in this checkout**
   (`tools.h`: added `double c1=1., double c2=1.` defaults, so the two-argument
   callers in `reprocess.C`/`globalFitRenormPF.C` keep meaning `g1 - g2`).
3. `reprocess.C`, `softrad3.C`, `globalFitL3Res.C` fail to compile:
   `tdrstyle_mod15.C` uses `lumi_136TeV` without declaring it. **Fixed in this
   checkout** (added `TString lumi_136TeV = "X fb^{-1}";` next to the other
   `lumi_*` globals; the 13.6 TeV macros overwrite it anyway).
4. With those fixes everything compiles, but `reprocess("Run2Test")` asserts
   immediately because `rootfiles/jecdataRun2TestData.root` is missing.
5. Following the comment in `mk_reprocess.C` ("Comment out if using archived
   jecdata[epoch].root"), the chain was rerun with `reprocess()` skipped on
   the archived `rootfiles/jecdataRun2Test.root`. `softrad3` ran, but every
   `TGraphErrors` it read came back empty, with 915 messages of the form
   `Could not find the StreamerInfo for version 4 of the class TGraph`.
   The archived file was written by ROOT 6.18.04 and contains **no TGraph
   StreamerInfo** at all; ROOT 6.32 changed TGraph to class version 5 and
   therefore cannot decode the version-4 payload. ROOT 6.30 and earlier still
   have TGraph version 4 and read it natively.
6. `globalFitSyst` then stopped on `../gamjet/files/GamHistosFill_data_2018ABCD_v19.root`
   (missing). With `doGamGains` and `doHadWfsr` switched off it segfaults on
   the first empty graph. `globalFitRenormPF` and `globalFitL3Res` were never
   reached; `globalFitL3Res` would also need the missing
   `rootfiles/drawDeltaJEC_Run2_vsUL4X.root`.
7. `rootfiles/jecdataRun2Test.root` was **restored from git** afterwards, because
   the ROOT 6.32 `UPDATE` had written empty FSR graphs into it.

**Bottom line:** to run this workflow you need (a) a ROOT ≤ 6.30 (or a CMSSW
environment of the DP-2021 era), and (b) the inputs listed in `MissedME.md` §1.
Logs of every attempt are in
`/private/tmp/claude-501/-Users-ravindrakumar-rverma-JME-JERC-jecsys/a8f7eae7-d2e8-4d15-b554-b2df879dec08/scratchpad/logs/`.

### 2.4 Related drivers

* `mk_reprocess_RunEpoch.C` — `root -l -b -q 'mk_reprocess_RunEpoch.C("2018ABCD")'`
  runs `mk_reprocess.C` for a chosen epoch.
* `mk_reprocessAndreyMultifit.C` — variant used for the multi-fit studies.
* `globalFitRun2.C`, `globalFitPulls.C`, `globalFitSettings.h` — newer Run-2
  legacy fit on top of the same `jecdata*.root` (not wired into `mk_reprocess.C`).
* `recombine.C` — builds `jecdataRun2TestData.root` (see §2.1).
* `softrad.C` — older alpha-extrapolation FSR (commented out in the driver).
* `Flavor.C/h` — flavour response/fraction lookup used by `reprocess.C`
  (reads `rootfiles/flavor/*.txt`; worked fine here).
* `multijet.C`, `compareJECdata.C`, `drawGamVsZmm.C`, `drawAvsB.C` — helper plots
  over `jecdata*.root`.

---

## 3. USER workflow — `test/` drawing macros

### 3.1 The path problem

The `test/mk_*.C` drivers load the JEC library as `CondFormats/...` (a path
relative to `jecsys/`) and the drawing macro as `drawUncertainty.C` (a path
relative to `test/`), and the macros `#include "CondFormats/..."` (relative to
`jecsys/`). So they fail from **both** directories as written. The working
invocation, from `jecsys/`, is:

```bash
root -l -b -q -e 'gROOT->SetMacroPath(".:test:"); gSystem->AddIncludePath("-I'"$PWD"'");' test/mk_drawUncertainty.C
```

(`mk_drawCMSresponse.C` is the odd one out: it uses `../CondFormats` and must be
run from inside `test/`.)

### 3.2 Results

| Driver | Input it reads | Result |
|---|---|---|
| `mk_drawUncertainty.C` → `drawUncertainty("TotalNoFlavorNoTime","AK5PFchs")` | `CondFormats/JetMETObjects/data/Winter14_V8_DATA_UncertaintySources_AK5PFchs.txt` | OK; prints `Min(0.32%): 153.25 Max(0.32%): 331`; draws `f1` on `c1` (no file saved) |
| `mk_drawSourceCorrelations.C` | same Winter14_V8 file (AK5PFchs, AK7PF) | OK; 6 files `pdf/drawSourceCorrelations_*_8TeV[_Eta13].pdf` |
| `mk_drawCMSresponse.C` | `../JERCProtoLab/Summer20UL/global_fit/Summer19UL17_RunH_VX_DATA_*_AK4PFchs.txt` | fails: directory not present |
| `mk_drawATLASresponse.C` | `CondFormats/JetMETObjects/data/Winter14_V5_MC_{L2Relative,L3Absolute}_AK5PFchs.txt` | fails: files not present (only `Winter14_V8_*` are) |
| `mk_compareJECversions.C` | `CondFormats/JetMETObjects/data/UL2017_ComplexL1_MC_*` and `UL2017v2_SimpleL1_MC_*` | fails: files not present |

`test/tdrstyle_mod14.C` is a private copy of the style file for these macros.

---

## 4. EXPERT workflow B — UncertaintySources (`mk_drawJetCorrectionUncertainty.C`)

```bash
root -l -b -q mk_drawJetCorrectionUncertainty.C      # ~2 min, worked end to end
```

* Code: `JECUncertainty.cpp/.hpp` (the uncertainty model, one method per
  source), `ErrorTypes.cpp/.hpp` (bit-mask enumeration of sources),
  `JetDefs.hpp`, and `drawJetCorrectionUncertainty.C` (loops over sources, draws,
  and writes the text files).
* Inputs: all from `CondFormats/JetMETObjects/data/`, currently hard-wired to
  **Autumn18 V17** (`Autumn18_V17_MC_L1FastJet/L1RC_AK4PFchs.txt`,
  `Autumn18_Run{A,B,C,D,ABCD}_V17_DATA_L{1,2,3,2L3Residual}_AK4PFchs.txt`, the
  `Autumn18_V17_L1L2*_Func3_*_L2Residual_pythia8_*` closure inputs, and
  `Winter14_V8_DATA_UncertaintySources_AK5PFchs.txt` for the 8 TeV reference).
  All present.
* Outputs: `txt/Autumn18_V18_DATA_Uncertainty_AK4PFchs.txt`,
  `txt/Autumn18_V18_DATA_UncertaintySources_AK4PFchs.txt` (the output tag
  `V18` is hard-coded in `drawJetCorrectionUncertainty.C` around line 1527) and
  105 plots `pdf/JECSource_<Source>_AK4PFchs[_Eta..|_Pt..|_E..].pdf`.
  `pdf/sysslides.tex` is the beamer template that includes those plots
  (`pdflatex pdf/sysslides.tex`, after deleting stale pdfs as the driver comment says).
* To change era/algorithm: edit the file-name block in `JECUncertainty.cpp`
  (lines ~200–530) and the output names in `drawJetCorrectionUncertainty.C`;
  the driver's second argument toggles writing the source files.

---

## 5. EXPERT workflow C — `mk_testSources.C`

```bash
root -l -b -q mk_testSources.C      # fails
```

* Purpose: check that the quadratic sum of the sources in a
  `*_UncertaintySources_*.txt` reproduces the `*_Uncertainty_*.txt` total, for
  one (pT, eta) point and in a loop; also checks SubTotal* and
  CorrelationGroup* subsets (`testSources.C`).
* Two blockers, see `MissedME.md` §3:
  1. The macro itself does not compile under ROOT 6: `exit();` without an
     argument and `nFailedTests` (a global of `testSources.C`) used in the
     unnamed macro.
  2. It expects `txt/Winter14_V5_DATA_{UncertaintySources,Uncertainty}_AK5PF.txt`,
     which are gitignored (`txt/*.txt`) and not in the checkout. The source-name
     lists in `testSources.C` only know `Summer13_V2/V5` and `Winter14_V5`, so
     the two `Summer16_03Feb2017_V7` files that *are* in `txt/` cannot be used
     without extending `testSources.C`.

---

## 6. Everything else at top level

| File(s) | What it is |
|---|---|
| `alcajme.C/h`, `mk_alcajme.C`, `drawAlCaJME.C` | Run-3 AlCaRaw / JMENANO MPF-MPFX studies (need `../data/AlCaRaw/skimmed_ntuple.root`) |
| `drawJMENANO.C` | Run-3 JMENANO L2Res / PF composition plots |
| `deriveL2ResNarrow.C`, `mk_deriveL2ResNarrow.C` | L2Res from single-jet triggers (needs `rootfiles/L3res_mumu_Run2016*.root`, `output-*-2b-Fall18V8-*.root`) |
| `drawUncEtaVsPt.C`, `mk_drawUncEtaVsPt.C` | 2D uncertainty map; expects `txt/Summer16_03Feb2017_V9_*` (only V7 present) |
| `drawOffsetPt.C`, `mk_drawOffsetPt.C` | offset vs pT from L1 files; note the driver loads `drawoffsetPt.C` (lower-case o), which only works on a case-insensitive filesystem |
| `mk_drawL2L3ResChi2Variants.C` + `minitools/drawL2L3ResChi2Variants.C` | chi2 variants of the L2L3Res fit |
| `compareJECdata.C`, `mk_compareJECdata.C` | compare two `jecdata*.root` (expects `rootfiles/jecdataG*.root`, not present) |
| `hotjets2016/2017/2018/Run2.C`, `dataquality.C`, `dqm.C` | hot-zone and data-quality maps |
| `jetflavor.C`, `drawJetFlavor.C`, `Flavor.C/h` | flavour response studies |
| `RhoVsNPV.C`, `drawOffsetPt.C` | pile-up / UE studies |
| `overlay_Dijet_Zjet*.py` | PyROOT overlay scripts (PyROOT not available here) |
| `tdrstyle_mod.C / _mod14.C / _mod15.C` | CMS TDR style; `_mod15` is the one `#include`d by the fit chain |
| `settings.h` | legacy inclusive-jet settings (lumi, algo), only used by old macros |
| `pdf/*.tex` | beamer templates that collect the pdfs (`jecslides`, `sysslides`, `multijetslides`, `l2resnslides`, `deltajecslides`) |
| `minitools/` | ~80 study macros; most say what they need in a `// Purpose:` header. The `mk_*` ones there are meant to be run from `jecsys/` as `root -l minitools/mk_x.C`. Notable: `mergeL2L3ResTextFiles.C` (builds the `textFiles/mergeL2L3ResTextFiles_<epoch>` inputs used by `reprocess.C`), `createL2L3ResTextFile.C`, `convertGlobalFitOutputToStandardTxt.sh`, `drawDeltaJEC.C` (builds `rootfiles/drawDeltaJEC_*.root`), `runAllIOVs.py` |

---

## 7. Local modifications made while running (uncommitted)

```
 M tdrstyle_mod15.C   # + TString lumi_136TeV = "X fb^{-1}";
 M tools.h            # diffGraphs(g1,g2,double c1=1.,double c2=1.)
```

Both are needed for anything that includes `tdrstyle_mod15.C` or `tools.h` to
compile. `rootfiles/jecdataRun2Test.root` was modified by the ROOT 6.32 run and
then restored (`git checkout -- rootfiles/jecdataRun2Test.root`); it is identical
to the committed version again. Generated, gitignored files left in place:
`txt/Autumn18_V18_*.txt`, `pdf/JECSource_*.pdf`, `pdf/drawSourceCorrelations_*.pdf`,
and the ACLiC `*.so/*.d/*.pcm` build products.
