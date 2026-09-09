# JERCSW ↔ ZbAnalysis synchronisation: Z(→μμ/ee)+jet L3Residual, Run 2 UL

Scope: ZmmJet and ZeeJet, years 2016Pre (APV/HIPM: B–F), 2016Post (F, G, H), 2017 (B–F), 2018 (A–D), AK4 jets.
Compared code states (both checked out under `JERC/Sync/`):

| Framework | Repo | HEAD |
|---|---|---|
| JERCSW (**JS**) | `gitlab.cern.ch/cms-analysis/jme/jerc-derivation/JERCSW` | `28b832f` "synchronising with Sami/KIT" (2026-09-04) |
| ZbAnalysis (**ZB**) | `gitlab.cern.ch/slehti/ZbAnalysis` | `d2b5713` "analyse.py: removed limit …" (2026-09-03) |

Paths are relative to the two package roots. JS = `Skim/` (RDataFrame skim of NanoAOD) + `Hist/` (C++ event loop, `RunL3ResidualZllJet.cpp`). ZB = `analyse.py` (driver, per-dataset parameter list) + `src/Analysis.cc` (ROOT `TSelector`, `Process()` at l.7054) + `plot_v3.py` (post-processing) + `NanoAODSkim/` (CRAB skim). "≠" marks a difference that changes the selected events or the response; "≈" marks one that is numerically negligible or an implementation detail. The comparison describes each code **as configured today**: JS `Hist/Inputs.py` runs the `Closure` stage for ZmmJet only (`Hist/Inputs.py:6-8,27-28`); ZB `analyse.py` defaults are `SMEARING=True`, `PILEUPREWEIGHT=False`, `GENWEIGHT=True`, `PSWEIGHT="-1"` (`analyse.py:35-47`).

DRAFT STATUS: written from a direct reading of both code bases; a multi-agent verification pass over every item is running and its corrections/additions will be folded in (see §18).

---

## 0. Executive summary — differences that will move the response

Ordered by expected impact on the derived L3Residual (data/MC ratio of ⟨R_MPF⟩, ⟨R_pT⟩ vs pT(Z)).

| # | Item | JERCSW | ZbAnalysis | Impact |
|---|---|---|---|---|
| 1 | **Input campaign and jet/MET collections** | JMENanoAODv9, `Jet` = AK4 **CHS**, MET from `RawMET` (PF, CHS-nano) (`Skim/input/SamplesNano_*_Data.json`, `Hist/cpp/GlobalFlag.cpp:254` AK4Chs→NanoVersion V9, `Skim/config/ReadConfigCommon.json` MetChs group) | Run 2 re-skimmed in Aug 2026 with the v14019 skim (`run3.job:34-37`) after "Run2 is now in nAODv15" (git `46dbf34`); Run 2 JEC text files are **AK4PFPuppi** (`analyse.py:725-790`), rho is `Rho_fixedGridRhoFastjetAll` (`src/Analysis.cc:~5990`), MET from **`RawPuppiMET`** (`src/Analysis.cc:6924,7578`). The NanoAODv15 dataset list is not in the repo (only the JMENanoAODv9 list, `NanoAODSkim/test/multicrab.py:69-183`). | **Very high.** As configured this is a CHS-vs-PUPPI comparison, not a selection comparison. Confirm the Jet collection in the v15 skims. |
| 2 | **Residual JEC on data** | L2Residual (derivation) or L2L3Residual (`Closure` stage, the current `Hist/Inputs.py`) chosen by `GlobalFlag.cpp:230-237`; L1FastJet+L2Relative always | `L2Relative×L2L3Residual` always on data (`analyse.py:725-790`, `src/Analysis.cc:6501-6558`); no L1 (PUPPI); the applied residual is stored as `p2res = 1/L2L3Res` for undoing (`src/L2ResHistograms.cc`) | High for a *derivation* sync: ZB has no "L2Residual only" mode. |
| 3 | **MET entering MPF** | Type-1 from `RawMET`: jets with μ-subtracted raw pT ≥ 10, corrected pT > 15, |η| < 5.2, EMF < 0.9; reference = L1FastJet on μ-subtracted raw; JER included on MC (`Hist/cpp/ScaleJet.cpp:67,103-165,188`, `Hist/cpp/ScaleMet.cpp:44,68-69`) | Type-1 from `RawPuppiMET` + Σ(raw − corr) over ΔR-cleaned jets with corrected pT > 15, no EMF/η cut, no μ-subtraction, no L1 (`src/Analysis.cc:6915-6985`) | High (R_MPF, MPFn, MPFu). |
| 4 | **|η(Z)| cut** | `|η(Z)| ≤ 1.3` (`Hist/config/PickZllJet.json:26`, `Hist/cpp/PickZllJet.cpp:305`) | none | High acceptance change; not a standard L3Res cut. |
| 5 | **Z kinematics** | pair closest to 91.1876, |Δm| ≤ 20, pT ≥ 15 (`PickZllJet.json:22-24`, `PickZllJet.cpp:303-304`) | pair closest to **90**, |Δm| < 20, pT ≥ **12** (`src/Analysis.cc:6866,6888,6890`) | Medium (edge of first pT bin, ±1.2 GeV mass shift). |
| 6 | **Lepton pT / η thresholds** | μ 20/20, |η| ≤ 2.3, |dxy| < 0.2, |dz| < 0.5; e 25/25, |η_SC| ≤ 2.4 with 1.4442–1.566 gap veto (`PickZllJet.json:3-19`, `PickZllJet.cpp:158-170,193`) | μ 20/**10**, |η| < 2.3; e 25/**15**, |η| < 2.4 (track η), **no gap veto**, no dxy/dz; applied to the two Z leptons only after pairing (`src/Analysis.cc:6184-6207`) | Medium at low pT(Z). |
| 7 | **Trigger-object matching** | none | every selected lepton must match a `TrigObj` of its flavour within ΔR < 0.3 (`src/Analysis.cc:6209-6231,6268,6384`) | Medium: extra per-lepton efficiency, not in JS. |
| 8 | **Zee HLT 2016** | `HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ` (`Hist/config/HltZeeJet.json:2`) | `HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL` (non-DZ) for all years (`analyse.py:684`) | Medium (2016 Zee data). 2017/18 agree (non-DZ). |
| 9 | **α definition and α cuts** | jet2 = 2nd cleaned jet with pT ≥ 12 (any η); α = pT(jet2)/pT(Z); hard `α < 1.0`; histograms for α < 1.0/0.5/0.2/0.1 (`RunL3ResidualZllJet.json:16-18`, `.cpp:213-214`) | jet2 = highest-pT remaining jet with pT ≥ 10 (any η); **α := 0 if pT(jet2) < 15**; no event-level α cut; histograms for α < 0.3 and α < 1.0 (`src/Analysis.cc:7476,7544-7547,8612,695`) | Medium: different α-selected samples; **no common α working point** (JS has no 0.3, ZB no 0.1/0.2/0.5). |
| 10 | **Response window and averaging** | events kept only if 0.3 < R_pT < 1.7 **and** 0.3 < R_MPF < 1.7 (`RunL3ResidualZllJet.json:20-21`, `.cpp:238-241`); ⟨R⟩ from TProfile | no cut; TH2 with y ∈ [−3.99, 5.99] step 0.02 (`src/Analysis.cc:717,1000`); ⟨R⟩ = `ProjectionY().GetMean()` per pT(Z) bin (`plot_v3.py:1354-1373`) | Medium: truncation bias on ⟨R⟩ differs. |
| 11 | **Jet–lepton cleaning** | `Jet_muonIdx1/2 == −1` (Zee: `electronIdx`) **and** ΔR(jet, ℓ) ≥ 0.4 to the pT-selected leptons (`PickZllJet.json:34-37`, `PickZllJet.cpp:383-413`) | ΔR(jet, ℓ) ≥ 0.3 to **all** ID'd+trigger-matched leptons (pT > 8 μ / > 15 e), no index check (`src/Analysis.cc:7286`, `6753-6766`) | Medium for MPFn/MPFu and jet2. |
| 12 | **Jet ID / PU ID on the probe** | TightLepVeto (`Jet_jetId ≥ 6` in v9) **and** tight PU ID for pT < 50 (bit 0 in UL2016, bit 2 in UL2017/18) (`Hist/cpp/PickJetId.cpp:121-129,147`) | `Jet_jetId ≥ 4` (tightLepVeto bit) on the leading jet only (`src/Analysis.cc:6801,7420`); no PU ID | Medium at pT(Z) < 50 (PU ID) — PU ID is not defined for PUPPI, so this follows from #1. |
| 13 | **JER smearing** | all jets; correctionlib `JERSmear` hybrid (ΔR < 0.2, |Δpt| < 3σ, deterministic seed); Summer20UL16(APV)_JRV3 / Summer19UL17_**JRV3** / Summer19UL18_JRV2, AK4PFchs (`Hist/config/ScaleJetLoaderSummer19ULNoUncAK4Chs.json:9-10,35-36,54-55,101-102`, `Hist/cpp/ScaleJetFunction.cpp:307-308,351`) | **only the first 3 jets** of the (ΔR-cleaned, NanoAOD-ordered) list (`src/Analysis.cc:6505,6536`); hybrid with same matching (`6598-6608`), fixed `mt19937` seed 92837465 (`5896`); Summer20UL16(APV)_JRV3 **AK4PFPuppi** / Summer19UL17_**JRV2 AK4PFchs** / Summer19UL18_JRV2 AK4PFPuppi (`analyse.py:732-733,742-743,765-766,786-787`) | Medium (MC only): 2017 version, PUPPI/CHS mix, and un-smeared jets ≥ 4 feed MPFn/MPFu. |
| 14 | **Rochester corrections** | data `kScaleDT`; MC `kSpreadMC` if a `GenDressedLepton` μ within ΔR < 0.2, else `kSmearMC` with seeded RNG (`Hist/cpp/ScaleMuonFunction.cpp:61-85`) | data `kScaleDT`; MC `kScaleMC × kExtra` (no gen matching); **no correction for pT < 26 GeV**, no extra smearing above 200 GeV (`src/MuonCorrections/CorrectionLib/src/MuonCorrection.cc:63-73`, `interface/MuonCorrection.h:15-22`) | Medium at low pT(Z) (10–26 GeV muons uncorrected in ZB). |
| 15 | **Electron energy scale/smearing** | none applied for V9 (`Hist/cpp/ScaleElectron.cpp:58-59`); v9 `Electron_pt` is already EGM-corrected in NanoAOD | none for Run 2 (`ElectronCorrection` parameter only for 2024, `analyse.py`); with NanoAODv15 inputs `Electron_pt` is uncorrected | Medium for Zee (data/MC scale mismatch in ZB) — to confirm for v15. |
| 16 | **MET filters** | applied to **data and MC** in the skim cut; 2016: goodVertices, globalSuperTightHalo2016, HBHENoise, HBHENoiseIso, EcalDeadCellTriggerPrimitive, BadPFMuon, eeBadSc; 2017/18: + ecalBadCalib (`Skim/config/ReadConfigCommon.json:144-171`, `Skim/cpp/RunChannel.cpp:~50-60`) | **data only** (`src/Analysis.cc:6160`); 2016: no `EcalDeadCellTriggerPrimitiveFilter` (mis-typed name, commented `analyse.py:699`); 2017/18: + `BadPFMuonDzFilter` (`analyse.py:695-716`) | Low–medium. |
| 17 | **Jet veto maps** | correctionlib `jetvetomaps.json.gz`, key `jetvetomap_hot` only, on the **probe**, data and MC (`Hist/config/PickEvent.json:4-26`, `Hist/cpp/PickEvent.cpp` passJetVetoMapOnProbe) | private `hotjets-UL16/17/18.root`; data maps include HEM15/16 (2018) and HEP17 (2017); **MC map only for 2016** (`src/JetvetoMap.cc:8-18`); applied to the leading jet (`src/Analysis.cc:7400`) | Low for |η| < 1.3; asymmetric data/MC treatment in ZB 2017/18. |
| 18 | **Pileup reweighting** | on: correctionlib `puWeights.json`, 69.2 mb (`Hist/config/ScaleEvent.json`, `Hist/cpp/ScaleEvent.cpp:113`) | **off by default** (`analyse.py:37`); MC events with μ > 100 vetoed (`src/Analysis.cc:7088`) | Low–medium (rho-dependent quantities, MPFu). |
| 19 | **Per-lepton SFs and prefiring** | ID×Iso×Trig SF per Z lepton, L1 prefiring for **2018 only** (`RunL3ResidualZllJet.cpp:254-263`, `ScaleEvent.cpp:116-121`) | none | Low for ratios; shape effects only. JS content has bugs (§14). |
| 20 | **MC sample and generator weight** | DY amc@NLO (`DYJetsMgNloPy8`), σ = 6077.22 pb, w = genWeight/Σw (`Skim/Inputs.py:93-104`, `SamplesNano_MapToXsecInPb.json`, `ScaleEvent.cpp:36,112`) | DY madgraphMLM + TTJets amc@NLO merged into one "MC" (`NanoAODSkim/test/multicrab.py`, `plot_v3.py:2244`); σ(DY) = **2124.08 pb** (`plot_v3.py:142`), σ(TT) = 496.1; w = genWeight·N/Σw (`src/GenWeight.cc:75`) | Low for ⟨R⟩ (MLM vs NLO shape differences and the tt̄ admixture matter more than normalisation). |
| 21 | **Binning / output** | TProfile of DB, MPF, MPF1, MPFn, MPFu, MPFnu vs pT(Z) in [15…1500] (20 bins) per α cut; probe |η| ≤ 1.3 only (`Hist/config/VarBin.json:4-7`, `Hist/cpp/HistL3Residual.cpp`, `HistAlpha.cpp`) | TH2 pT(Z) [12,15,…,1500] × R per (α < 0.3/1.0) × |η| bins 0–1.3, 0–2.5, 2.5–3, 3–5, 4.7–5 (`src/Analysis.cc:614,695,744`), plus HDM bisector profiles (`L2ResHistograms.cc`) | ≈ (same pT edges above 15). |

Blocking/runnability items (details §14): JS `Hist/POG/EGM/` is absent so the ZeeJet Hist step cannot start (`ScaleElectronLoader.cpp` throws on missing files) and only ZmmJet/Closure is enabled; ZB references Run 2 AK4PFPuppi JEC/JER text files that are not in the repository (only AK4PFchs Summer19/20UL files are tracked in `src/CondFormats/JetMETObjects/data`, `*.txt` is git-ignored).

---

## 1. Inputs: campaign, collections, samples

### 1.1 NanoAOD campaign and physics-object collections

| Item | JS | ZB | |
|---|---|---|---|
| NanoAOD | JMENanoAODv9 (UL MiniAODv2), DAS names in `Skim/input/SamplesNano_<year>_{Data,MC}.json` | `NanoAODSkim/test/multicrab.py:69-183` lists JMENanoAODv9; but the analysis code was migrated to NanoAODv15 semantics (`git log 46dbf34 "disabled all 'year < 2020' conditions as Run2 is now in nAODv15"`, `24716a3` JEC update to AK4PFPuppi, `5adf52d`), and the Aug-2026 Run 2 skims are `multicrab_ZbAnalysis_v14019_Run201{6BCDEF,6FGH,7BCDEF,8ABCD}_202608…` (`run3.job:34-37`). Dataset list for these skims is not in the repo. | ≠ |
| Jet collection | AK4 CHS (`AK4Chs` → NanoVersion V9, `GlobalFlag.cpp:254`; branch group `AK4Common`+`MetChs`, `ReadConfigCommon.json`) | `Jet` collection corrected with AK4PFPuppi Summer19UL text files (`analyse.py:725-790`) → treated as AK4 PUPPI | ≠ |
| Rho | `fixedGridRhoFastjetAll` (V9) → `skimT->Rho` (`ReadConfigCommon.json:8`) | `Rho_fixedGridRhoFastjetAll` (v12+ naming; the `fixedGridRhoFastjetAll` branch is commented out, `src/Analysis.cc:~5985-5995`) | ≈ |
| MET | `RawMET`, `MET`, `ChsMET` kept; Type-1 rebuilt from `RawMET` (`ScaleMet.cpp:44`) | `RawPuppiMET`/`PuppiMET` bound; `RawMET`/`ChsMET`/`MET` branch addresses commented out (`src/Analysis.cc:~6100-6115`); Type-1 rebuilt from `RawPuppiMET` (`6924`) | ≠ |

### 1.2 Data primary datasets

Both use DoubleMuon (Zmm), DoubleEG (2016/17) and EGamma (2018) for Zee. In the JMENanoAODv9 lists:

| Era | JS `SamplesNano_*_Data.json` | ZB `multicrab.py` (v9) | |
|---|---|---|---|
| 2016B ver1 (HIPM) | included (`-v2` μ, `-v2` e) | commented out (`:143,150`) | ≈ (tiny lumi) |
| 2016B ver2, C, D, E, F-HIPM | `-v2` for μ, `-v2` e (Bv2 e `-v1`) | `-v1` for μ and e (F e `-v2`) | ≈ check DAS suffixes |
| 2016F (non-HIPM), G, H | `-v2` F, `-v1` G/H | same | = |
| 2017 B–F | `-v1` | `-v1` | = |
| 2018 A–D | `-v1` | `-v1` | = |

Luminosity per era used by JS for MC normalisation: `Skim/input/SamplesNano_MapToLumiInFb.json` (2016PreBv1 = 2016PreBv2 = 2.914 fb⁻¹ — likely a placeholder; 2016PreF 2.718, 2016PostF 0.418). ZB takes the per-dataset lumi from `lumi.json` written by `NanoAODSkim/test/lumicalc.py` (brilcalc, normtag_PHYSICS) into the multicrab directory (`analyse.py` `loadLuminosity`). The 2016F HIP split is at run 278800/278801 in both (ZB JSON file names `Cert_277932-278800_…_Run2016F_HIP.txt` / `Cert_278801-278808_…_HIPfixed.txt`; JS uses the DAS HIPM/non-HIPM datasets).

### 1.3 MC

| Item | JS | ZB | |
|---|---|---|---|
| Signal | `DYJetsToLL_M-50 amcatnloFXFX` (`DYJetsMgNloPy8`), Herwig7 MLM as alternative sample (`SamplesNano_*_MC.json`, `Skim/Inputs.py:93-104`) | `DYJetsToLL_M-50 madgraphMLM` (v9 list `multicrab.py:86,112,…`; amc@NLO "Pilot" entries commented as too small); herwig7 task blacklisted (`analyse.py:1309`) | ≠ generator (NLO vs LO-MLM) |
| Background | none | `TTJets amcatnloFXFX` processed and merged into "MC" together with DY (`plot_v3.py:2244` `mergeDatasets("MC","^(?!Data).*")`) | ≠ |
| σ | 6077.22 pb (`SamplesNano_MapToXsecInPb.json`) | `xsecs["DYJetsToLL_M_50"] = 2124.08` (FEWZ reference in comment), `xsecs["TTJets"] = 496.1` (`plot_v3.py:110,142`); which key the v15 DY task maps to depends on its multicrab task name | ≠ (affects only the tt̄ admixture and data/MC yield plots) |
| Event count for normalisation | `nEventsNano` from the skim `Runs`/`hEventsPerJobFromNano`, `normGenEventSumw` cached per sample (`Hist/jerc.cpp`, `RunsTree.cpp`); w = 1000·L·σ/N × genWeight/Σw (`ScaleEvent.cpp:36,112`) | `nev = getEvents()` from the skim counters; `norm = lumi·xsec/nev` at plotting (`plot_v3.py:407-430`); per-event genWeight × N/Σw from `GenWeight.json` when present (`src/GenWeight.cc:75`) | ≈ |

---

## 2. Skim-level selection

| Item | JS (`Skim/`) | ZB (`NanoAODSkim/test/NanoAOD_ZbAnalysisSkim.py`) | |
|---|---|---|---|
| Event cut | `(filters AND) && (triggers OR)`; missing filters default true, missing triggers default false (`Skim/cpp/RunChannel.cpp` `buildFullCut`, `applyDefaultValues`) | none: trigger OR (`:101-151`) and MET cleaning (`:161-172`) are computed but the `return False` lines are commented (`:154-155,174-175`) → every event is kept | ≈ (analysis re-applies cuts) |
| Branches kept | explicit lists (`ReadConfigCommon.json`, `ReadConfigZmmJet.json`, `ReadConfigZeeJet.json`) incl. `Jet_muonSubtrFactor`, `Jet_puId`, `L1PreFiringWeight_*`, `GenDressedLepton_*` | full NanoAOD content; `analyse.py:~830-960` enables only used branches at analysis time | ≈ |
| Filters applied to MC | yes (part of the skim cut) | no (`src/Analysis.cc:6160`) | ≠ |

---

## 3. HLT

| Year | Channel | JS (`Hist/config/Hlt*.json`, also in the skim `ReadConfig*.json:25-32`) | ZB (`analyse.py:665,668,684`) | |
|---|---|---|---|---|
| 2016 | Zmm | `HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ` | same | = |
| 2017, 2018 | Zmm | `HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8` | same | = |
| 2016 | Zee | `HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ` | `HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL` | ≠ |
| 2017, 2018 | Zee | `HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL` | same | = |

Both require the trigger on MC as well (`PickHltOr::pass` for all samples; `getTriggerDecision` for all). ZB additionally matches each selected lepton to any `TrigObj` with `TrigObj_id == 13/11` within ΔR < 0.3 (`src/Analysis.cc:6209-6231`), dropping unmatched leptons before Z building (`:6268,6384`); JS has no trigger-object matching. 2017H (`HLT_HIMu17`) is a ZB-only special case.

---

## 4. MET filters, Golden JSON, pileup, vetoes

| Item | JS | ZB | |
|---|---|---|---|
| MET filters 2016 | goodVertices, globalSuperTightHalo2016, HBHENoise, HBHENoiseIso, **EcalDeadCellTriggerPrimitive**, BadPFMuon, eeBadSc (`ReadConfigCommon.json:144-151`) | goodVertices, globalSuperTightHalo2016, HBHENoise, HBHENoiseIso, BadPFMuon, eeBadSc (`analyse.py:695-703`); EcalDeadCell line is commented and mis-named | ≠ |
| MET filters 2017/2018 | + ecalBadCalib; **no** BadPFMuonDz (`:153-171`) | + EcalDeadCell, **BadPFMuonDz**, ecalBadCalib (`analyse.py:706-716`) | ≠ |
| Applied to | data and MC | data only (`Analysis.cc:6160`) | ≠ |
| Golden JSON | one file per year: `Cert_271036-284044_…Legacy2016`, `Cert_294927-306462_…UL2017`, `Cert_314472-325175_…Legacy2018` (`PickEvent.json:7,14,21,28`) | per-era split files of the same certifications (`NanoAODSkim/data/Cert_*_Run201XY.txt`), applied at CRAB and again in `Lumimask` (`src/Lumimask.cc`) | = |
| PU reweighting | correctionlib `puWeights.json` nominal, 69.2 mb (`ScaleEvent.json`, `ScaleEvent.cpp:113`) | off by default (`analyse.py:37`); when on: ratio of `PileUp.root` histograms (pileupCalc, 69.2 mb) (`src/PileupWeight.cc`) | ≠ (as configured) |
| μ for data | not used | `getAvgPU(run, ls)` from `pileup_20XX.txt` (`parsePileUpJSON2.h`), 69200 μb | ≈ |
| MC PU veto | none | `Pileup_nTrueInt > 100` vetoed (`Analysis.cc:7088`); events with weight > 1000 vetoed (`:7091`) | ≈ |
| PV–GenVtx match | available, commented out (`RunL3ResidualZllJet.cpp:153`) | none | = |
| Jet veto map | correctionlib `Summer19UL16_V1`/`UL17_V1`/`UL18_V1`, key `jetvetomap_hot`, evaluated on the probe (`PickEvent.json:4-26`, `PickEvent.cpp` `passJetVetoMapOnProbe`), data and MC | `hotjets-UL16.root: h2hot_ul16_plus_hbm2_hbp12_qie11 (data) / h2hot_mc (MC)`; `hotjets-UL17_v2.root: h2hot_ul17_plus_hep17_plus_hbpw89 (data only)`; `hotjets-UL18.root: h2hot_ul18_plus_hem1516_and_hbp2m1 (data only)` (`src/JetvetoMap.cc:8-18`); evaluated on the leading jet (`Analysis.cc:7400`) | ≠ (HEM/HEP17 in ZB data only; MC unvetoed 2017/18) |
| HEM 2018 | `HemVeto.json` exists but is not used by `RunL3ResidualZllJet` | via the data veto map only | ≈ |
| Extra veto | none | "jet spikes": leading jet pT < 70 and 2.65 < |η| < 2.964 vetoed (`Analysis.cc:7424`) | ≈ for |η| < 1.3 |

---

## 5. Muons (ZmmJet)

| Item | JS (`PickZllJet.json:13-19`, `PickZllJet.cpp:163-171,187-197`) | ZB (`Analysis.cc:6233-6300,6184-6207`) | |
|---|---|---|---|
| ID | `Muon_tightId == 1` | `Muon_tightId` | = |
| Isolation | `Muon_pfRelIso04_all < 0.15` | `Muon_pfRelIso04_all < 0.15` (`:6241,6255`) | = |
| |η| | ≤ 2.3 at preselection | none at object level; < 2.3 required for the two Z leptons after pairing (`:6189`) | ≈ (ordering) |
| pT | lead (highest-pT preselected μ) ≥ 20, all others ≥ 20 (`:193`) | object pT > 8 (`:6236`); after Z pairing: one Z lepton > 20 and both > 10 (`:6187-6188`) | ≠ |
| Impact parameters | |dxy| < 0.2, |dz| < 0.5 | none | ≠ small |
| Trigger match | none | required, ΔR < 0.3 to `TrigObj_id == 13` (`:6268`) | ≠ |
| Rochester file | `RoccoR2016aUL` (2016Pre), `RoccoR2016bUL` (2016Post), `RoccoR2017UL`, `RoccoR2018UL` (`ScaleMuon.json:3,20,…`) | same files, chosen by multicrab era `2016BCDEF`/`2016FGH` (`analyse.py:734,744,767,789`) | = |
| Rochester method | data `kScaleDT`; MC `kSpreadMC(genPt)` if `GenDressedLepton` μ within ΔR < 0.2 else `kSmearMC(nL, u)`, RNG seeded by event (`ScaleMuonFunction.cpp:61-85`) | data `kScaleDT` (pT ≥ 26 only); MC `kScaleMC × kExtra(nL, u)` for 26 ≤ pT ≤ 200, u seeded from (φ, event, lumi) (`MuonCorrection.cc:63-73`, `RoccoRHelper.cc`) | ≠ |
| Corrected before pT cuts / Z pairing | yes (applyCorrections on preselected muons, then `selectLeptonsByPt`, `pickTag`) | yes (inside `getMuons`) | = |
| Muon SFs | ID×Iso×Trig per Z lepton (see §12) | none | ≠ (weights) |

## 6. Electrons (ZeeJet)

| Item | JS (`PickZllJet.json:3-9`, `PickZllJet.cpp:150-161`) | ZB (`Analysis.cc:6316-6417,6191-6193`) | |
|---|---|---|---|
| ID | `Electron_cutBased ≥ 4` (tight) | `Electron_cutBased == 4` (`:6321`) | = |
| Isolation | (in cutBased ID) | `Electron_pfRelIso03_all < 1.0` (`:6342`, effectively none) | ≈ |
| η | |η_SC| ≤ 2.4 (`eta + deltaEtaSC`), gap 1.4442–1.566 vetoed | |η| < 2.4 on track η after pairing; no gap veto | ≠ |
| pT | 25/25 | object pT > 15; after pairing one > 25 and both > 15 | ≠ |
| Trigger match | none | required, ΔR < 0.3 to `TrigObj_id == 11` (`:6384`) | ≠ |
| Energy scale/smearing | none applied for V9 (`ScaleElectron.cpp:58-59`); NanoAODv9 `Electron_pt` already carries the EGM corrections | none for Run 2 (`eleCorFound` false; `ElectronCorrection` only set for 2024 in `analyse.py`) | ≠ if v15 electrons are uncorrected — confirm |
| Electron SFs | ID×Reco×Trig from `POG/EGM/*.root` (files absent) | none | ≠ (weights) |
| dxy/dz | none | none (block commented, `:6323-6331`) | = |

## 7. Z candidate

| Item | JS (`PickZllJet.json:22-28`, `PickZllJet.cpp:262-330`) | ZB (`Analysis.cc:6865-6893,7180-7290`) | |
|---|---|---|---|
| Lepton multiplicity | 2 ≤ N(pT-selected leptons) ≤ 3, else no tag (`nLepMin/nLepMax`) | 2 ≤ N(ID'd, trigger-matched leptons of the channel flavour) ≤ 3 (`:7190`); both charges present (`:7202`) | ≈ |
| Pairing | OS pairs; keep the pair with |m − 91.1876| minimal among pairs passing |Δm| ≤ 20, pT ≥ 15, |η(Z)| ≤ 1.3 | all l⁺l⁻ pairs; keep the pair with |m − 90| minimal; **then** require pT ≥ 12 and |Δm| < 20 (`:6866-6890`) | ≠ |
| Mass window | 71.19–111.19 | 70–110 | ≠ |
| pT(Z) | ≥ 15 | ≥ 12 | ≠ |
| |η(Z)| | ≤ 1.3 | none | ≠ |
| Gen Z (MC) | `GenDressedLepton` OS pair, pT ≥ 12, ΔR(gen Z, reco Z) < 0.2 (`PickZllJet.cpp:505-550`) | `GenPart` with pdgId = ±13/±11 (no status requirement), pair closest to 90 (`:6419-6437,7230-7245`) | ≈ |

---

## 8. Jets and corrections

### 8.1 JEC

| Item | JS | ZB | |
|---|---|---|---|
| Source | correctionlib `POG/JME/<year>_UL/jet_jerc_WithL2ResNoUnc.json.gz` (`ScaleJetLoaderSummer19ULNoUncAK4Chs.json:3,29,48,95`, selected in `ScaleJetLoader.cpp:22`) | text files `src/CondFormats/JetMETObjects/data/*.txt` via `FactorizedJetCorrector` (`Analysis.cc:5325-5900`) | ≈ |
| Tags | Summer19UL16APV_V7 (RunBCD / RunEF), Summer19UL16_V7 (RunFGH), Summer19UL17_V5 (RunB…F), Summer19UL18_V5 (RunA…D), **AK4PFchs** | same tags and era split, **AK4PFPuppi** (`analyse.py:725-790`) | ≠ algorithm |
| Levels, MC | L1FastJet(area, η, pT, ρ) × L2Relative (`ScaleJet.cpp:103,120`) | L2Relative only (no L1/L3 files given) | ≈ (PUPPI has no L1) |
| Levels, data | + L2Residual (derivation) **or** + L2L3Residual (Closure; current `Inputs.py`) (`ScaleJet.cpp:136,149`, `GlobalFlag.cpp:230-237`) | + L2L3Residual always | ≠ for derivation |
| Raw pT | `pt·(1 − rawFactor)` | same (`:6511`) | = |
| Jets corrected | all | all in the ΔR-cleaned list (jets removed by lepton cleaning stay at NanoAOD pT and are not in MET either) | ≈ |

### 8.2 JER (MC)

| Item | JS (`ScaleJetFunction.cpp:190-370`) | ZB (`Analysis.cc:6501-6622`) | |
|---|---|---|---|
| Inputs | Summer20UL16APV_JRV3, Summer20UL16_JRV3, Summer19UL17_JRV3, Summer19UL18_JRV2 (AK4PFchs) | Summer20UL16APV_JRV3, Summer20UL16_JRV3 (AK4PFPuppi), Summer19UL17_**JRV2** (**AK4PFchs**), Summer19UL18_JRV2 (AK4PFPuppi) | ≠ 2017 |
| Which jets | all | first 3 entries of `jetSelection` (`smearNMax = 3`, `:6505,6536`) — NanoAOD order after ΔR cleaning, before `ptOrder` | ≠ |
| Method | correctionlib `JERSmear`: scaling if gen match (ΔR < 0.2, |Δpt| < 3σ·pT), else stochastic; σ at JES-corrected pT; deterministic seed from (run, lumi, event) | hybrid: `CF = 1 + (SF−1)(pT−pT_gen)/pT` if matched (ΔR < 0.2, |pT−pT_gen|/pT < 3σ), else `N(0, σ√(SF²−1))`; σ at JES-corrected pT; `mt19937` fixed seed 92837465 | ≈ |
| SF lookup | (η, "nom") | (pT, η) → η-binned SF | = |

### 8.3 Jet selection, ID, cleaning

| Item | JS (`PickZllJet.cpp:352-490`, `PickJetId.cpp`) | ZB (`Analysis.cc:7280-7480,6781-6850`) | |
|---|---|---|---|
| Candidate jets | corrected pT ≥ 12; `Jet_muonIdx1 == −1 && Jet_muonIdx2 == −1` (Zee: electronIdx); min ΔR to any pT-selected lepton ≥ 0.4 | all jets; remove ΔR < 0.3 to any ID'd+trigger-matched lepton of the channel flavour (pT > 8 μ / > 15 e) (`:7286`) | ≠ |
| Probe (jet1) | highest-pT candidate; must pass TightLepVeto ID (+ tight PU ID if pT < 50) and |η| ≤ 1.3, else event dropped (`:443-451`) | highest-pT jet with pT ≥ 12 and |η| < 5 (`:6827-6828,7390`); must pass `Jet_jetId ≥ 4` (`:7420`) and the veto map (`:7400`) | ≠ (η range; PU ID) |
| jet2 (for α) | 2nd highest-pT candidate (pT ≥ 12, any η, no ID) | highest-pT remaining jet with pT ≥ 10 (`jetPt(…,10)` `:7476`, `getLeadingJetIndex(…,1)`), any η, no ID | ≈ |
| Jetn (for MPFn) | Σ of all candidate jets except jet1 (jet2 included), pT ≥ 12, index-cleaned but **not** ΔR-cleaned (`:459-480`) | Σ of ΔR-cleaned jets with pT > 15 minus jet1 (`:7519`, `jets_notLeadingJet`) | ≠ |
| Jet ID semantics | v9 `Jet_jetId ≥ 6` = tight ∧ tightLepVeto; PU ID bit 0 (UL2016) / bit 2 (UL2017/18) for pT < 50 (`PickJetId.cpp:121-129,143-147`) | `Jet_jetId ≥ 4` → tightLepVeto bit set (`:6801`); no PU ID | ≈ for the ID, ≠ for PU ID (n/a for PUPPI) |

---

## 9. MET / Type-1 recipe

| Step | JS (`ScaleJet.cpp:60-215`, `ScaleMet.cpp`) | ZB (`Analysis.cc:6915-6985`) | |
|---|---|---|---|
| Start | `RawMET` (PF) | `RawPuppiMET` (`:6924`) | ≠ |
| Jet set | all jets with `ptRawMinusMuon ≥ 10 && ptFinalForMet > 15 && |η| < 5.2 && (neEmEF+chEmEF) < 0.9` (`:188`) | ΔR-cleaned, pT ≥ 10 pre-filtered jets with corrected pT > 15 (`:6964`) | ≠ |
| Correction subtracted | `ptFinalForMet − ptL1ForMet` on μ-subtracted raw (L1FastJet reference; final includes L2Rel, residual, JER) (`ScaleMet.cpp:68-69`) | `corr − raw` (full correction incl. JER for ≤ 3 jets; no L1) (`:6980`) | ≠ (CHS vs PUPPI recipe) |
| Lepton propagation | `p4CorrMet += p4RawTag − p4Tag` intended, but no-op (§14) | none | = (effectively) |
| Unclustered (MPFu) | `−(MET + Z + jet1 + Jetn)` with Jetn as in §8.3 (`MathHdm.cpp:76-79`) | `−(MET + Σ cleaned jets pT>15 + Z)` (`:7584`) | ≈ definitionally the same, ≠ through the jet sets |

---

## 10. Event selection and cutflow order

JS (`RunL3ResidualZllJet.cpp:147-241`): HLT → golden JSON → (gen-vertex match, commented) → exactly one Z (after Rochester/electron corrections) → jets corrected, probe found (ID, |η| ≤ 1.3) → |Δφ(Z, probe) − π| < 0.44 (`.json:15`) → veto map on probe → α computed (histograms before cut) → α < 1.0 → 0.3 < R_pT < 1.7 and 0.3 < R_MPF < 1.7 → fill.

ZB (`Analysis.cc:7054-7620`): PU weight, μ ≤ 100 (MC), weight ≤ 1000 → golden JSON (data) → genWeight/PSWeight → HLT → MET filters (data) → 2–3 leptons, both charges → Z (pT ≥ 12, |m−90| < 20) → lepton pT/η cuts on the Z pair → ΔR-clean jets, JEC(+JER), pT-order → leading jet pT ≥ 12, |η| < 5 → veto map → `phiBB = |Δφ − π| < 0.44` (`:7415`) → jet ID on leading jet → spike veto → sub-leading jet from pT ≥ 10 → α (α = 0 if pT(jet2) < 15) → MET, responses → fill (no α cut, no response cut).

Ordering-dependent consequences: (i) JS applies |η| ≤ 1.3 and ID when choosing the probe, ZB applies ID after choosing the leading jet — same final set for the |η| < 1.3 bin; (ii) ZB's lepton |η| < 2.3/2.4 and pT cuts are applied after pairing, so an event with a forward or soft muon chosen into the pair is vetoed rather than re-paired; (iii) ZB cleans jets against all ID'd leptons (also those not in the Z), JS only against the pT-selected ones; (iv) in ZB jets failing ΔR cleaning are excluded from the type-1 MET sum, in JS they are included subject to EMF < 0.9 and μ-subtraction.

---

## 11. Response mathematics and histogramming

| Quantity | JS (`MathHdm.cpp:108-118`) | ZB (`Analysis.cc:7588-7597`) | |
|---|---|---|---|
| R_pT (DB) | pT(probe)/pT(Z) | `leadingJet.Pt()/Zboson.Pt()` | = |
| R_MPF | 1 + MET⃗·Z⃗/pT(Z)² | `1 + MET·(cosφ Zx + sinφ Zy)/pT(Z)²` | = |
| MPF1 | 1 − (Z⃗+probe⃗)·Z⃗/pT² | `R_MPFjet1 = −jet1⃗·Z⃗/pT²` (without the "1 +") | ≈ (offset by 1) |
| MPFn | −Jetn⃗·Z⃗/pT² | `−jets_notLeadingJet⃗·Z⃗/pT²` | = formula, ≠ jet set |
| MPFu | −(unclustered)·Z⃗/pT² | `−METuncl⃗·Z⃗/pT²` | = formula |
| MPFnu | MPFn + 1.1·MPFu (`:80`) | HDM extras with 1/0.92 (`L2ResHistograms.cc`) | ≈ |
| MPFX | tag rotated by +π/2 | `R_MPFx`, `R_MPFjet1x` | = |
| Storage | TProfile vs pT(Z) [15…1500]; TProfile2D vs (η_probe, pT(Z)); TH1 R ∈ [0, 2]; α-cut profiles (`HistL3Residual.cpp`, `HistAlpha.cpp`, `VarBin.json:4-7,58`) | TH2 pT(Z) [12…1500] × R ∈ [−3.99, 5.99] (0.02) per α-cut × |η|-bin; TH3 with μ or |η|; HDM bisector `TProfile2D`s (`p2m0/p2m2/p2mn/p2mu` vs (η, pT_tag)) (`Analysis.cc:614,717,1000-1004`, `L2ResHistograms.cc`) | ≈ |
| ⟨R⟩ extraction | TProfile mean (window 0.3–1.7 applied at fill) | `ProjectionY(ibin).GetMean()` over [−3.99, 5.99] (`plot_v3.py:1354-1373`); x = bin centre | ≠ |
| Gen-level | `histObjGenReco` (gen tag vs reco tag pT, gen probe vs probe pT), `GenDressedLepton` Z | `R_pTGen`, `R_MPFGen`, `R_GMPF`, `JESRpTGen`, flavour-split by `Jet_partonFlavour` | ≈ |

---

## 12. Event weights

| Component | JS (`ScaleEvent.cpp`, `RunL3ResidualZllJet.cpp:247-266`) | ZB (`Analysis.cc:7070-7130`, `plot_v3.py:407-430`) | |
|---|---|---|---|
| Generator | genWeight/Σ(genWeight) | genWeight·N/Σ(genWeight) if `GenWeight.json` exists, else raw genWeight (`GenWeight.cc:75`) | ≈ |
| L·σ/N | at fill (`lumiWeight_`, `:36`) | at plotting (`normalizeToLumi`) | ≈ |
| PU | correctionlib nominal | off (default) | ≠ |
| Lepton SF | ID×Iso×Trig (μ) / ID×Reco×Trig (e), per Z lepton | none | ≠ |
| L1 prefiring | 2018 only (`:116-121`) | none | ≠ |
| PS weights | only for the Isr/Fsr systematic runs (`Systematics.cpp`) | `PSWEIGHT = "-1"` → none | = |
| HEM weight | `WeightBuilderZll::setHemWeight` exists, not called | none | = |

---

## 13. Per-year matrix of versioned inputs

| Input | 2016Pre | 2016Post | 2017 | 2018 |
|---|---|---|---|---|
| **JS** JEC data | Summer19UL16APV_RunBCD_V7 / RunEF_V7 (chs) | Summer19UL16_RunFGH_V7 | Summer19UL17_Run{B,C,D,E,F}_V5 | Summer19UL18_Run{A,B,C,D}_V5 |
| **ZB** JEC data | same tags, AK4PFPuppi, chosen by era `2016BCDEF` + run B/C/D vs E/F (`analyse.py:722-729`) | Summer19UL16_RunFGH_V7 Puppi | Summer19UL17_Run{B..F}_V5 Puppi | Summer19UL18_Run{A..D}_V5 Puppi |
| **JS** JEC MC | Summer19UL16APV_V7 | Summer19UL16_V7 | Summer19UL17_V5 | Summer19UL18_V5 |
| **ZB** JEC MC | Summer19UL16APV_V7 Puppi (L2Relative only) | Summer19UL16_V7 Puppi | Summer19UL17_V5 Puppi | Summer19UL18_V5 Puppi |
| **JS** JER | Summer20UL16APV_JRV3 chs | Summer20UL16_JRV3 chs | Summer19UL17_JRV3 chs | Summer19UL18_JRV2 chs |
| **ZB** JER | Summer20UL16APV_JRV3 Puppi | Summer20UL16_JRV3 Puppi | Summer19UL17_JRV2 **chs** | Summer19UL18_JRV2 Puppi |
| Rochester (both) | RoccoR2016aUL | RoccoR2016bUL | RoccoR2017UL | RoccoR2018UL |
| **JS** PU | `Collisions16_UltraLegacy_goldenJSON` (preVFP json) | (postVFP json) | `Collisions17_UltraLegacy_goldenJSON` | `Collisions18_UltraLegacy_goldenJSON` |
| **ZB** PU | off; `pileup_2016.txt` for data μ | same | `pileup_2017.txt` | `pileup_2018.txt` |
| Golden JSON (both) | Legacy2016 (JS one file; ZB per era) | Legacy2016 | UL2017 | Legacy2018 |
| **JS** MET filters | 7 (incl. EcalDeadCell) | 7 | 8 (+ecalBadCalib) | 8 |
| **ZB** MET filters (data) | 6 (no EcalDeadCell) | 6 | 8 (+EcalDeadCell, BadPFMuonDz, ecalBadCalib) | 8 |
| HLT Zmm (both) | Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ | same | …_DZ_Mass8 | …_DZ_Mass8 |
| HLT Zee | JS DZ / ZB non-DZ | JS DZ / ZB non-DZ | non-DZ (both) | non-DZ (both) |
| **JS** veto map | Summer19UL16_V1 `jetvetomap_hot` | same | Summer19UL17_V1 hot | Summer19UL18_V1 hot |
| **ZB** veto map | UL16 data `h2hot_ul16_plus_hbm2_hbp12_qie11`, MC `h2hot_mc` | same | UL17 data `…_plus_hep17_plus_hbpw89`, MC none | UL18 data `…_plus_hem1516_and_hbp2m1`, MC none |
| **JS** prefiring | none (bug: should be applied) | none | none | `L1PreFiringWeight_Nom` |
| **ZB** prefiring | none | none | none | none |
| Lumi (JS, fb⁻¹) | Bv1 2.914, Bv2 2.914, C 2.621, D 4.286, E 4.065, F 2.718 | F 0.418, G 7.653, H 8.74 | B 4.823, C 9.664, D 4.252, E 9.278, F 13.54 | A 14.0, B 7.1, C 6.94, D 31.93 |

---

## 14. Code-health findings relevant to the sync

### JERCSW
1. `Hist/POG/EGM/` does not exist; `ScaleElectronLoader::loadEleSfHists` throws on a missing file → the ZeeJet Hist step cannot run until the EGM SF/SS files are added (`Hist/cpp/ScaleElectronLoader.cpp:57-70`, `Hist/config/ScaleElectronLoader.json`).
2. `Hist/Inputs.py:6-8,27-28`: stage `Closure` (data get L2L3Residual) and ZmmJet only. For the derivation sync switch to `Derivation` and enable ZeeJet.
3. `RunL3ResidualZllJet.cpp:176,224`: `p4RawTag` is copied after `applyCorrections` already overwrote `Muon_pt`/`Electron_pt`, so `p4CorrMet += p4RawTag − p4Tag` adds zero.
4. `ScaleEvent.cpp:116-121`: L1 prefiring weight applied for 2018 only; ECAL prefiring affects 2016/2017 and 2018's weight is muon-only. Likely inverted.
5. `Hist/config/ScaleMuon.json:12-16`: ID SF histogram `NUM_TrkHighPtID_DEN_TrackerMuons` while the selection is `tightId`; trigger SF is the single-muon `IsoMu24/27` efficiency applied to each of the two muons although the dimuon path is used.
6. `RunL3ResidualZllJet.json:17-19`: `minPtJet2InAlpha` and `maxTagEta` are read but unused (`.cpp:216` commented; the η(Z) cut comes from `PickZllJet.json:26`).
7. `PickZllJet.cpp:459-480`: Jetn skips the ΔR(jet, ℓ) cleaning used for jet1/jet2.
8. `Skim/input/SamplesNano_MapToLumiInFb.json:3-4`: 2016PreBv1 and Bv2 both 2.914 fb⁻¹ — check.
9. `ScaleJetFunction.cpp:232-237`: JER SF evaluated with (η, syst) for all algorithms (FIXME comment) — correct for the Run 2 UL SF payloads, revisit for Puppi/Run 3.

### ZbAnalysis
1. `analyse.py:725-790` references Run 2 `Summer19UL*_AK4PFPuppi` JEC and `Summer20UL16*_JRV3_*_AK4PFPuppi` JER text files that are not in the repository (`ls src/CondFormats/JetMETObjects/data | grep -i puppi` finds only Run 3 files; `.gitignore` excludes `*.txt`). The 2017 MC JER files are the AK4PFchs ones (`:765-766`). `Init()` checks existence only for L1 files (`Analysis.cc:~5815`).
2. NanoAODv15 Run 2 dataset list and the skim configuration that produced `multicrab_ZbAnalysis_v14019_Run201*_202608*` are not in the repo (`NanoAODSkim/test/multicrab.py` is the JMENanoAODv9 list).
3. `Analysis.cc:6160`: MET filters return true for MC; `analyse.py:699` names `EcalDeadCellTriggerPrimitiveFilter` without the `Flag_` prefix and is commented → 2016 data lack this filter.
4. `src/JetvetoMap.cc:13-18`: no MC map for 2017/2018 (data-only veto).
5. `Analysis.cc:6505,6536`: JER smearing only for the first three entries of the cleaned jet list (order = NanoAOD order, i.e. pT-ordered before cleaning); jets beyond the third stay unsmeared but enter MPFn/MPFu and type-1 MET.
6. `MuonCorrection.cc:63-73`: Rochester scale not applied below 26 GeV and `kExtra` used instead of `kSpreadMC`/`kSmearMC`; the `kExtra` smearing is applied to all MC muons regardless of gen matching.
7. `Analysis.cc:6801`: `Jet_jetId ≥ 4`; under NanoAODv15 semantics JME recommends recomputing the ID from PF fractions (JS does so for V15 in `PickJetId.cpp:158-260`).
8. `analyse.py:37`: `PILEUPREWEIGHT = False`; `Analysis.cc:7088`: MC μ > 100 veto; `:7091` weight > 1000 veto.
9. `NanoAOD_ZbAnalysisSkim.py:154-155,174-175`: the skim keeps all events (trigger and cleaning disabled).
10. `plot_v3.py:142`: `xsecs["DYJetsToLL_M_50"] = 2124.08` pb (vs 6077.22 pb NNLO inclusive); relevant for the DY/tt̄ admixture and yield plots only.
11. `Analysis.cc:6342`: electron isolation cut `pfRelIso03 < 1.0` is a no-op; `:6321` `cutBased == 4` (fine, 4 is the maximum).
12. `plot_v3.py:1354-1373`: ⟨R⟩ is a plain mean over the TH2 y-range [−3.99, 5.99]; x is the bin centre, not ⟨pT(Z)⟩.

---

## 15. Open questions

1. Which NanoAOD campaign and `Jet` collection are in the Aug-2026 ZB Run 2 skims (v14019)? If NanoAODv15 with `Jet` = AK4 PUPPI, the sync must first agree on CHS vs PUPPI (JS can run AK4Puppi, `Skim/Inputs.py:12`).
2. Where do the Run 2 AK4PFPuppi JEC/JER text files used by ZB come from (JECDatabase? which versions)?
3. Are NanoAODv15 Run 2 electrons scale-corrected in `Electron_pt`? (ZB applies no correction; JS applies the EGM json only for V15.)
4. Is the |η(Z)| ≤ 1.3 cut in JS intentional?
5. Which α working point and response window should define the common baseline (JS 1.0 hard + 0.3–1.7; ZB 0.3/1.0 with no window)?
6. Should the derivation sync be done with L2Residual only on data in both codes (ZB currently applies L2L3Residual and stores 1/L2L3Res for undoing)?

---

## 16. Proposed common baseline (for discussion)

1. Inputs: same NanoAOD campaign and jet algorithm (decide JMENanoAODv9/CHS or NanoAODv15/PUPPI); DoubleMuon, DoubleEG/EGamma; DY amc@NLO (or MLM in both), no tt̄ in the response plots.
2. HLT: Zmm `Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ` (2016) / `_DZ_Mass8` (2017–18); Zee `Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ` (2016) / `_IsoVL` (2017–18); no trigger-object matching (or in both).
3. MET filters: JetMET UL list incl. `BadPFMuonDzFilter`, applied to data and MC.
4. Muons: tightId, pfRelIso04 < 0.15, |η| < 2.3, pT > 20/10 (decide), dxy/dz cuts in both or neither; Rochester on all muons: data `kScaleDT`, MC `kSpreadMC` (gen-matched) else `kSmearMC`.
5. Electrons: cutBased tight, |η_SC| < 2.4 with 1.4442–1.566 veto, pT > 25/15 (decide); same scale/smearing treatment.
6. Z: |m − 91.1876| < 20, pT > 15, exactly one OS pair, 2 ≤ N_ℓ ≤ 3, **no η(Z) cut** unless justified.
7. Jets: same JEC tags; data L2Residual only for derivation; JER hybrid on all jets with the same versions; clean ΔR(jet, ℓ) < 0.4 (and `muonIdx/electronIdx == −1`); probe TightLepVeto, |η| < 1.3, pT > 12; PU ID off in both (CHS) or n/a (PUPPI).
8. Δφ: |Δφ − π| < 0.44; α = pT(jet2)/pT(Z), jet2 = 2nd cleaned jet with pT > 15 (α = 0 otherwise); common α set {0.3, 1.0} ∪ {0.1, 0.2, 0.5}; same response window in both (or none).
9. MET: agree on one Type-1 recipe (raw MET source, jet thresholds, μ-subtraction/L1 for CHS) and propagate lepton corrections in both or neither.
10. Weights: PU on in both; no lepton SFs / prefiring in the sync stage (or identical ones).
11. Histograms: TProfile (or TH2 + mean over the same window) of DB, MPF, MPF1, MPFn, MPFu vs pT(Z) in [15, 20, …, 1500].

---

## 17. What already agrees

HLT Zmm paths; Zee 2017/18 path; JEC tags and era splits; JER 2016/2018 versions; Rochester files; Golden JSON certifications; muon ID/isolation; electron ID WP; Δφ cut 0.44; jet2 without ID; R_pT and R_MPF formulae; pT(Z) binning above 15 GeV; both apply the trigger to MC; both correct leptons before pairing/pT cuts.

## 18. Verification status

Pending: multi-agent adversarial verification of every row above (workflow `zjet-sync-jercsw-zbanalysis`); this section will list corrections and additions.
