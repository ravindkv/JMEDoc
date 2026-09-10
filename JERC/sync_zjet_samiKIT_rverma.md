# JERCSW ↔ ZbAnalysis (KITcomparison) synchronisation: Z(→μμ/ee)+jet residual JEC, Run 2 UL

Scope: ZmmJet and ZeeJet, AK4 CHS, years 2016Pre (APV/HIPM: B–F), 2016Post (F, G, H), 2017 (B–F), 2018 (A–D).

| Framework | Checkout | HEAD |
|---|---|---|
| JERCSW (**JS**) | `JERC/Sync/JERCSW` | `28b832f` "synchronising with Sami/KIT" (2026-09-04) |
| ZbAnalysis (**ZB**) | `JERC/Sync/ZbAnalysis_KITcomparison`, branch `KITcomparison` | `c3f72fb` "Merge origin/master into KITcomparison" (**2021-08-19**) |

Paths are relative to the two package roots. JS = `Skim/` (RDataFrame skim of NanoAOD) + `Hist/` (C++ event loop, `Hist/cpp/RunL3ResidualZllJet.cpp`). ZB = `NanoAODSkim/` (CRAB NanoAODTools skim) + `analyse.py` (driver; passes year, trigger and filter names, pileup histograms to the selector) + `src/Analysis.cc` (ROOT `TSelector`, `Process()` at l.4790–6727) + `plot_v2.py` (normalisation, merging, ⟨R⟩ extraction). "≠" marks a difference that changes the selected events or the response; "≈" marks one that is numerically negligible or an implementation detail; "=" agrees.

Both codes are described **as configured at HEAD**: JS `Hist/Inputs.py` runs the `Closure` stage, AK4Chs, ZmmJet only, all four years (`Hist/Inputs.py:6-9,11-15,25-34,46-58`); ZB `analyse.py` has `LEPTONFLAVOR = 11` (Zee), `MULTIPROCESSING = True`, `TEST = False`, `maxEvents = -1` (`analyse.py:19-35`) and no other switches — JER smearing, PU reweighting, JEC re-application and the per-event `printSync` dump are unconditional in the C++.

This document supersedes `sync_samiPuppi_raviChs.md`, which compared JS with the 2026 `master` of ZbAnalysis (NanoAODv15/PUPPI inputs). The KITcomparison branch is the 2021 CHS code prepared for the KIT sync and differs from `master` in many cuts (see §18).

---

## 0. Executive summary — differences that will move the response

Ordered by expected impact on the derived residual (data/MC ratio of ⟨R_MPF⟩, ⟨R_pT⟩ vs pT(Z)).

| # | Item | JERCSW | ZbAnalysis (KITcomparison) | Impact |
|---|---|---|---|---|
| 1 | **Input NanoAOD campaign** | JMENanoAODv9 on UL MiniAODv2 (`Skim/input/SamplesNano_*_{Data,MC}.json`); `AK4Chs → NanoVersion::V9` (`Hist/cpp/GlobalFlag.cpp:252-258`) | `NanoAODSkim/test/multicrab.py:68-167` lists **UL MiniAODv1 NanoAODv2** (72 hits for `NanoAODv2`, 0 for `NanoAODv9`); the selector reads `Electron_cutBased_Fall17_V1` (`src/Analysis.cc:4109,4296`) and the auto-generated `src/BaseSelector.h:88` still contains that pre-v8 branch; the skim requires `Flag_BadPFMuonDzFilter` (`NanoAODSkim/test/NanoAOD_ZbAnalysisSkim.py:161`), which only exists from v9 | **High / blocking**: the repo does not pin one campaign. Confirm which NanoAOD the ZB skims actually are (the user's expectation is v9). Same physics content (CHS `Jet`, `RawMET`, `ChsMET`) in either case, but electron ID branch and `Jet_jetId`/`Jet_puId` semantics differ between v7-era and v9. |
| 2 | **Certified-lumi (Golden JSON) on data** | applied in Hist for data (`Hist/config/PickEvent.json:7,14,21,28`, `Hist/cpp/PickEvent.cpp:100-127`) | **not applied anywhere at HEAD**: the CRAB `lumiMask` lines are commented (`NanoAODSkim/test/multicrab.py:664-666`), `crab_cfg.py` has none, `PSet.py:7` `lumisToProcess` commented, no JSON code in `src/Analysis.cc`; the JSON is used only for brilcalc lumi (`lumicalc.py:34,89-91`) and pileupCalc (`pileup.py:75-78`) | **High** for data unless the skims were produced with an edited cfg — confirm. |
| 3 | **Type-1 MET entering R_MPF** | `RawMET` (PF) − Σ_jets (pT^{L1L2L3(+Res)(+JER)} − pT^{L1FastJet}) on **μ-subtracted raw** pT, jets with pT_raw,μ-sub ≥ 10, pT_corr > 15, |η| < 5.2, EMF < 0.9, **no jet ID** (`Hist/cpp/ScaleJet.cpp:67,116,187-192`, `Hist/cpp/ScaleMet.cpp:43-79`) | **`ChsMET`** (raw CHS MET) − Σ_jets (pT^{L1L2L3Res(+JER)} − pT^{**L1RC**}) over the **ΔR-cleaned, tightLepVeto-ID'd** `jetSelection` with pT_corr > 15, any η, no EMF veto, no μ-subtraction (`src/Analysis.cc:4664,4706,4712,4939-4946,5050,5121`) | **High** (R_MPF, MPFn, MPFu). Four independent differences: MET seed (CHS vs PF), offset reference (L1RC vs L1FastJet), jet set (ID'd vs all, EMF), muon handling. |
| 4 | **Residual JEC on data** | L1FastJet × L2Relative × **L2Residual** (Derivation) or × **L2L3Residual** (Closure = current `Inputs.py`) (`Hist/cpp/GlobalFlag.cpp:233-238`, `Hist/cpp/ScaleJet.cpp:135-149`) | L1FastJet × L2Relative × L3Absolute × **L2L3Residual always** (`src/Analysis.cc:3981-3986,4461-4470`); no "L2Residual only" mode | High for a *derivation* sync (ZB is a closure-type setup). |
| 5 | **JEC versions** | Summer19UL16APV_V7, Summer19UL16_V7, **Summer19UL17_V5**, Summer19UL18_V5, AK4PFchs via correctionlib `jet_jerc_WithL2ResNoUnc.json.gz` (`Hist/config/ScaleJetLoaderSummer19ULNoUncAK4Chs.json`) | Summer19UL16APV_V7, Summer19UL16_V7, **Summer19UL17_V6**, Summer19UL18_V5, AK4PFchs txt files (`src/Analysis.cc:3880-3941`) | Medium (2017 only). |
| 6 | **|η(Z)| cut** | `|η(Z)| ≤ 1.3` (`Hist/config/PickZllJet.json:26`, `Hist/cpp/PickZllJet.cpp:305`) | none (only in UE/PU-study fills) | High acceptance change; not a standard cut. |
| 7 | **Δφ(Z, jet1)** | `|Δφ − π| < 0.44` (`Hist/config/RunL3ResidualZllJet.json`, `.cpp:203-204`) | `|Δφ − π| < 0.34` (`src/Analysis.cc:5033-5035`) | Medium (MPFn/MPFu, α-dependence). |
| 8 | **Response window** | keep only `0.3 < R_pT < 1.7` **and** `0.3 < R_MPF < 1.7` (`RunL3ResidualZllJet.cpp:236-241`) | keep only **`R_pT ≥ 0.5`** (`src/Analysis.cc:5341`), no upper bound, no R_MPF cut; ⟨R⟩ = mean over y ∈ [−3.99, 5.99] (`src/Analysis.cc:275-276`, `plot_v2.py:1229-1238`) | Medium: different truncation bias, especially in R_MPF at low pT(Z). |
| 9 | **JER smearing (MC)** | correctionlib `JERSmear` **hybrid** (scaling if gen match ΔR < 0.2, |Δpt| < 3σ; else stochastic), all jets, seeded per event; JR: Summer20UL16(APV)_JRV3, **Summer19UL17_JRV3**, Summer19UL18_JRV2 (`Hist/cpp/ScaleJetFunction.cpp:258-398`, config `:9-10,35-36,54-55,101-102`) | **stochastic only**, no gen matching ("Following the example by KIT"), all jets, `mt19937` seed 92837465; JR: Summer20UL16(APV)_JRV3, **Summer19UL17_JRV2**, Summer19UL18_JRV2 (`src/Analysis.cc:4490-4509,3989-3996`) | Medium (MC only): resolution tails and 2017 version. |
| 10 | **Probe-jet ID / PU ID** | TightLepVeto (`Jet_jetId ≥ 6` in v9) **and** tight PU ID for pT < 50 (bit 0 UL2016, bit 2 UL2017/18), probe only (`Hist/cpp/PickJetId.cpp:109-148`, `PickZllJet.cpp:443-446`) | `Jet_jetId ≥ 4` on **all** jets in `jetSelection` (`src/Analysis.cc:4570,4946`); **no PU ID** | Medium at pT(Z) < 50; also changes jet2 and MET jet sets. |
| 11 | **Jet–lepton cleaning** | `Jet_muonIdx1/2 == −1` (Zee: `electronIdx`) **and** ΔR(jet, ℓ) ≥ 0.4 to the pT-selected leptons (`PickZllJet.json:34-37`, `PickZllJet.cpp:383-420`) | ΔR(jet, ℓ) ≥ 0.3 to **all** selected leptons of **both flavours** (μ tight iso pT > 20, e tight pT > 25) (`src/Analysis.cc:4859-4862,4939,4552-4564`) | Medium for MPFn/MPFu and jet2. |
| 12 | **Rochester corrections** | data `kScaleDT`; MC `kSpreadMC(genPt)` if `GenDressedLepton` μ within ΔR < 0.2 else `kSmearMC` (`Hist/cpp/ScaleMuonFunction.cpp:60-87`); applied **before** pT cuts | data `kScaleDT`; MC **always `kSmearMC`** (gen-matching loop is empty, `src/Analysis.cc:4265-4272`), `rand()` seed; applied **after** the pT/η/ID cuts (`:4246-4277`); silently disabled if `roccor.Run2.v5/` is absent (`:136-142`) — **directory not in repo** | Medium (Zmm MC scale/resolution); confirm the files exist on the running machine. |
| 13 | **Electrons** | pT 25/25, `|η_SC| ≤ 2.4` with 1.4442–1.566 gap veto, `Electron_cutBased ≥ 4` (`PickZllJet.json:2-11`, `PickZllJet.cpp:151-162`) | pT 25/25, `|η| < 2.4` (track η, no gap veto), `Electron_cutBased_Fall17_V1 == 4`, **signed** dxy/dz cuts (0.05/0.10 EB, 0.10/0.20 EE), `miniPFRelIso_all < 1.0` (no-op), massless 4-vector (`src/Analysis.cc:4292-4363`) | Medium for Zee (ID version, gap, IP). |
| 14 | **HLT Zmm 2017/2018** | `HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8` (`Hist/config/HltZmmJet.json:3-4`) | OR of `HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ`, `HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL_DZ`, `HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8` (`analyse.py:328-331`) | Medium: different (and partly prescaled) path set; lumi must be computed for the OR. 2016 agrees. |
| 15 | **HLT Zee 2016** | `…_IsoVL_DZ` (`Hist/config/HltZeeJet.json:2`) | OR of `…_IsoVL` and `…_IsoVL_DZ` for all years (`analyse.py:346-347`) | Medium (2016 Zee data); 2017/18 effectively agree. |
| 16 | **MET filters** | skim cut, **data and MC**: 2016 7 flags incl. `EcalDeadCellTriggerPrimitive`, `eeBadSc`; 2017/18 + `ecalBadCalib` (`Skim/config/ReadConfigCommon.json:143-172`, `Skim/cpp/RunChannel.cpp:46-62`) | skim: AND of goodVertices, globalSuperTightHalo2016, HBHENoise, HBHENoiseIso, BadPFMuon, **BadPFMuonDz**, data and MC (`NanoAOD_ZbAnalysisSkim.py:156-164`); analysis: data only (`src/Analysis.cc:4207`) and **OR-ed** (`:4214`) so `EcalDeadCellTP`, `ecalBadCalib`, `eeBadSc` are effectively not required | Low–medium. |
| 17 | **Generator weight** | genWeight/⟨genWeight⟩ (`Hist/cpp/ScaleEvent.cpp:112`) | **none** — `genWeight` never read; nominal weight = PU weight only (`src/Analysis.cc:4805`, grep `genWeight` → comments only) | Medium for aMC@NLO FxFx DY (negative-weight events counted positive). |
| 18 | **MC composition and normalisation** | DY amc@NLO only, σ = 6077.22 pb, lumi hard-coded 19.5/16.8/41.5/59.8 fb⁻¹ (`Hist/cpp/GlobalFlag.cpp:443-453`, `Skim/input/SamplesNano_MapToXsecInPb.json`) | DY amc@NLO **+ TTJets amc@NLO** merged into one "MC" (`plot_v2.py:2070`), σ(DY) = 6077.22, σ(TT) = 496.1 (`plot_v2.py:104,134`), lumi from brilcalc per dataset (`lumicalc.py`) | Low for ⟨R⟩; tt̄ admixture matters for MPF tails. |
| 19 | **Per-lepton SFs, prefiring** | ID×Iso×Trig per Z lepton (MC), L1 prefiring **2018 only** (`RunL3ResidualZllJet.cpp:257-264`, `ScaleEvent.cpp:116`) | none | Low for ratios; JS content has bugs (§15). |
| 20 | **Jet veto maps** | correctionlib `Summer19UL16/17/18_V1`, `jetvetomap_hot`, probe only, data **and** MC (`Hist/config/PickEvent.json:3-26`, `Hist/cpp/PickEvent.cpp:170-195`) | private `hotjets-UL16/17_v2/18.root`; data maps include HEP17 (2017) and HEM15/16 (2018); **MC map only for 2016** (`src/JetvetoMap.cc:3-41`); leading jet only (`src/Analysis.cc:5026-5028`) | Low for |η| < 1.3; asymmetric data/MC in ZB 2017/18. |
| 21 | **Probe |η| and binning** | probe |η| ≤ 1.3 required (`PickZllJet.cpp:448-453`); TProfile vs pT(Z) [15…1500] | probe |η| ≤ 2.5 (`src/Analysis.cc:4578,5018`), histograms for |η| ∈ (0, 1.3) and (0, 2.5) (`:293`); TH2 pT(Z) [12, 15, …, 1500] × R (`:218,275-276,518`) | ≈ for the 0–1.3 bin (same pT edges ≥ 15). |
| 22 | **α** | jet2 = 2nd ΔR/idx-cleaned jet, pT ≥ 12, **no ID**, any η; α = pT2/pT(Z); hard `α < 1.0` (`RunL3ResidualZllJet.cpp:212-214`); α histograms for α < 1.0/0.5/0.2/0.1 binned in **probe pT** (`Hist/cpp/HistAlpha.cpp:90-158`) | jet2 = 2nd **tightLepVeto** jet of `jetSelection`, any η; `α = 0 if pT2 < 15` (`src/Analysis.cc:5038,5094-5097`); only `α < 1.0` histograms exist (`bins_alpha = {0.3, 1.0}`, `:248,5683`) | ≈ (both effectively α < 1.0); no common α < 0.3 histogram. |

Runnability: JS `Hist/POG/EGM/` is git-ignored and absent, so the ZeeJet Hist step throws (`Hist/cpp/ScaleElectronLoader.cpp:58-61,89-95`); only ZmmJet/Closure is enabled. ZB: `roccor.Run2.v5/` absent (Rochester silently off), `Cert_*Run2016F_HIP*.txt` and `Custommix.txt` absent, `LEPTONFLAVOR` must be edited by hand for Zmm, every event is dumped to stdout (`printSync`, `src/Analysis.cc:5220`; `verbose = true` in `recalculateMET`, `:4669` — three dumps per event).

---

## 1. Inputs: campaign, collections, samples

### 1.1 Campaign and collections

| Item | JS | ZB | |
|---|---|---|---|
| NanoAOD | JMENanoAODv9 (data `…UL201X_MiniAODv2_JMENanoAODv9-vN`, MC `RunIISummer20UL1XNanoAODv9-20UL1XJMENano…`) | `multicrab.py:68-167`: `…UL2018_MiniAODv1_NanoAODv2-v1`, `RunIISummer19UL18NanoAODv2`, `RunIISummer20UL16NanoAODAPVv2` etc.; code reads v7-era `Electron_cutBased_Fall17_V1`; skim reads v9-only `Flag_BadPFMuonDzFilter` | ≠ (unpinned; confirm) |
| Jet collection | `Jet` = AK4 PF CHS; raw pT = `Jet_pt·(1−rawFactor)` (`Hist/cpp/ScaleJet.cpp:43`) | same (`src/Analysis.cc:4459`); JEC txt `*_AK4PFchs.txt` | = |
| Rho | `fixedGridRhoFastjetAll` (`Hist/cpp/SkimAdapter.cpp:95-96`) | `fixedGridRhoFastjetAll` (`src/Analysis.cc:4464`) | = |
| MET | `RawMET`, `MET`, `ChsMET` kept; Type-1 from `RawMET` | `ChsMET` (default R_MPF), `MET_pt` (`R_MPFfromType1`), `RawMET` (`R_MPFPF`) (`src/Analysis.cc:4664-4667`) | ≠ (see §10) |

### 1.2 Data primary datasets

Both: DoubleMuon (Zmm), DoubleEG 2016/2017 and EGamma 2018 (Zee). ZB also lists SingleMuon (eμ control, `LEPTONFLAVOR = −13`) and 2017H low-PU.

| Era | JS (`Skim/input/SamplesNano_*_Data.json`) | ZB (`multicrab.py`) | |
|---|---|---|---|
| 2016 B ver1/ver2 HIPM, C, D, E, F-HIPM | JMENanoAODv9 `-v2` (Bv2 DoubleEG `-v1`) | `datasets2016ULAPV` (`:119-151`), NanoAODv2 `-v1`; 2016F-HIPM with `Cert_277932-278800_…_Run2016F_HIP.txt` (file absent) | ≈ (same eras) |
| 2016 F, G, H | `-v2` F, `-v1` G/H | `datasets2016UL` (`:153-167`), F `-v2`, G/H `-v1`; F with `Cert_278801-278808_…HIPfixed.txt` (absent) | ≈ |
| 2017 B–F | `-v1` | `-v1` (`:90-107`) | ≈ |
| 2018 A–D | `-v1` | DoubleMuon B `-v2`, others `-v1`; EGamma `-v1` (`:68-82`) | ≈ |

2016Pre/2016Post separation: JS by year key; ZB by **two multicrab directories** whose names must contain exactly `Run2016BCDEF` or `Run2016FGH` (`multicrab.py:700-742`, `src/Analysis.cc:3853-3869,3880-3911`); `year` is "2016" in both (`analyse.py:466-471`). A combined `Run2016BCDEFGH` directory (as in `readme.txt:14`) gets no JEC prefix and exits.

### 1.3 MC

| Item | JS | ZB | |
|---|---|---|---|
| Signal | `DYJetsToLL_M-50 amcatnloFXFX-pythia8` (`DYJetsMgNloPy8`), one per year (`Skim/input/SamplesNano_*_MC.json:6`) | `DYJetsToLL_M-50 amcatnloFXFX-pythia8`, RunIISummer19UL17/18NanoAODv2, RunIISummer20UL16(APV)NanoAODv2 (`multicrab.py:84,109,150,166`) | = generator |
| Background | none | `TTJets amcatnloFXFX-pythia8` merged into "MC" (`multicrab.py:86,111,151,167`; `plot_v2.py:2070 mergeDatasets("MC","^(?!Data).*")`) | ≠ |
| σ | 6077.22 pb (`SamplesNano_MapToXsecInPb.json:2-3`) | 6077.22 pb (`plot_v2.py:134`), TT 496.1 (`:104`); `analyse.py:48-80` xsec table is dead code (inside a string) | = |
| Lumi | hard-coded per year 19.5/16.8/41.5/59.8 fb⁻¹ (`Hist/cpp/GlobalFlag.cpp:443-453`); per-era table in `Skim/input/SamplesNano_MapToLumiInFb.json` (Bv1 = Bv2 = 2.914, unused in Hist) | brilcalc per dataset, normtag_PHYSICS, from the golden JSON (`lumicalc.py:10,23-25,34,89-96`) → `lumi.json` → `configInfo/lumi`; plot uses Σ over inputs (`plot_v2.py:351-369`) | ≈ |
| N for normalisation | DAS event count `nEventsNano` (`Hist/cpp/SkimFile.cpp:116-117`); w = 1000·L·σ/N × genWeight/⟨genWeight⟩ (`Hist/cpp/ScaleEvent.cpp:36,112`) | counter "Skim: All events" (unweighted count, `plot_v2.py:336-337`); `norm = L·σ/N` at plotting; no genWeight | ≠ (genWeight) |

---

## 2. Skim-level selection

| Item | JS (`Skim/`) | ZB (`NanoAODSkim/test/NanoAOD_ZbAnalysisSkim.py`) | |
|---|---|---|---|
| Event cut | `(filters AND) && (triggers OR)`, same for data and MC (`Skim/cpp/RunChannel.cpp:46-62,227`); missing filters → true, missing triggers → false (`:68-78`) | trigger OR (`:99-151`, every existing path of all three year blocks) AND 6 MET flags (`:156-164`), data and MC | ≈ |
| Trigger list (skim) | ZmmJet: the analysis path only (`Skim/config/ReadConfigZmmJet.json:23-33`); ZeeJet: `Skim/config/ReadConfigZeeJet.json:24-34` | wide OR incl. `Mu17`, `Mu19`, `IsoMu24_eta2p1`, `Ele17_Ele12…`, `Ele23_Ele12…(_DZ)`; `HLT_HIMu17` present → accept all (`:131-132`) | ≈ (analysis re-applies) |
| Object preselection | none | none | = |
| Branches kept | explicit lists (`Skim/config/ReadConfigCommon.json`, `ReadConfigZmmJet.json`, `ReadConfigZeeJet.json`) incl. `Jet_muonSubtrFactor`, `Jet_puId`, `L1PreFiringWeight_*`, `GenDressedLepton_*`; Runs tree copied | full NanoAOD (no `branchsel`), `PostProcessor(..., cut="", modules=[SkimModule()])` (`:181`) | ≈ |
| JEC at skim | none | none | = |
| Golden JSON at skim | n/a (applied in Hist) | intended via CRAB `lumiMask`, but commented out (`multicrab.py:664-666`, `PSet.py:7`) | ≠ (see §4) |
| Counters/PU | `Runs` tree sums | `configInfo/SkimCounter`, `configInfo/pileup` (`Pileup_nTrueInt` before cuts, `:55,92-93`) | ≈ |

---

## 3. HLT (analysis level)

| Year | Channel | JS (`Hist/config/HltZmmJet.json`, `HltZeeJet.json`) | ZB (`analyse.py:327-351`) | |
|---|---|---|---|---|
| 2016 | Zmm | `HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ` | same | = |
| 2017, 2018 | Zmm | `HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8` | `HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ` ∨ `HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL_DZ` ∨ `HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8` (+ `HLT_HIMu17` for 2017H) | ≠ |
| 2016 | Zee | `HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ` | `HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL` ∨ `…_IsoVL_DZ` | ≠ |
| 2017, 2018 | Zee | `HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL` | `…_IsoVL` ∨ `…_IsoVL_DZ` | ≈ (DZ ⊂ non-DZ) |

Application: both a plain OR, required on **data and MC** (JS `Hist/cpp/PickHltOr.cpp:17-25`, `RunL3ResidualZllJet.cpp:147`; ZB `src/Analysis.cc:4184-4194,4841-4843`). Neither does trigger-object matching (ZB `TrigObj_*` exist only in `BaseSelector.h`, never bound). No per-trigger thresholds or lumi weighting in either (JS `Hist/cpp/ConfigHlt.cpp:67-89` uses a plain list for Zll). JS aborts if a trigger branch is missing (`Hist/cpp/SkimHlt.cpp:36`); ZB only warns (`src/Analysis.cc:4046-4049`).

---

## 4. MET filters, Golden JSON, pileup, vetoes

| Item | JS | ZB | |
|---|---|---|---|
| MET filters 2016 | goodVertices, globalSuperTightHalo2016, HBHENoise, HBHENoiseIso, EcalDeadCellTriggerPrimitive, BadPFMuon, eeBadSc (`ReadConfigCommon.json:143-151`), data+MC, AND | skim (data+MC, AND): goodVertices, globalSuperTightHalo2016, HBHENoise, HBHENoiseIso, BadPFMuon, BadPFMuonDz (`skim:156-164`); analysis (data only, **OR**): goodVertices, globalSuperTightHalo2016, HBHENoise, HBHENoiseIso, BadPFMuon, eeBadSc (`analyse.py:356-365`, `src/Analysis.cc:4206-4216`) | ≠ (no EcalDeadCell; eeBadSc ineffective; BadPFMuonDz extra) |
| MET filters 2017/18 | + ecalBadCalib (`:153-171`) | skim as above; analysis (OR): goodVertices, globalSuperTightHalo2016, HBHENoise, HBHENoiseIso, EcalDeadCellTriggerPrimitive, BadPFMuon, ecalBadCalib (`analyse.py:367-378`) | ≠ (EcalDeadCell/ecalBadCalib ineffective because of the OR) |
| Filters re-applied in Hist/analysis | no (skim only; `grep Flag_ Hist/cpp` empty) | yes, data only, OR-ed | ≈ |
| Golden JSON | one file per year, data only (`PickEvent.json:7,14,21,28`; `PickEvent.cpp:100-127`): Legacy2016, UL2017, Legacy2018 | per-era slices of the same three files generated by `NanoAODSkim/data/make201{6,7,8}jsons.py`; **not applied** at HEAD (§0 #2) | ≠ |
| PU reweighting | on: correctionlib `puWeights.json` nominal, `Collisions1X_UltraLegacy_goldenJSON` (`Hist/config/ScaleEvent.json`, `ScaleEvent.cpp:113`) | on (no switch): ratio of `PileUp.root:pileup` (pileupCalc, 69.2 mb, 100 bins) to skim `configInfo/pileup`, summed over the whitelisted datasets (`src/PileupWeight.cc:29-43`, `src/Analysis.cc:4805`, `analyse.py:103-121,261-272`); events with weight ≤ 0 dropped (`:4809`) | ≈ (same recipe, different implementation) |
| μ for data | not used | `getAvgPU(run, ls)` from `pileup_20XX.txt`, 69200 μb (`src/parsePileUpJSON2.h:23,140`; `src/Analysis.cc:5217`) — histograms only | ≈ |
| PV–GenVtx match | available, commented out (`RunL3ResidualZllJet.cpp:153`) | none | = |
| Jet veto map | correctionlib `Summer19UL16_V1`/`UL17_V1`/`UL18_V1`, `jetvetomap_hot`, probe only, data+MC, after Δφ (`RunL3ResidualZllJet.cpp:208`) | `hotjets-UL16.root` data `h2hot_ul16_plus_hbm2_hbp12_qie11` / MC `h2hot_mc`; `hotjets-UL17_v2.root` data `h2hot_ul17_plus_hep17_plus_hbpw89`; `hotjets-UL18.root` data `h2hot_ul18_plus_hem1516_and_hbp2m1`; **no MC map 2017/18** (`src/JetvetoMap.cc:3-41`); leading jet only, before Δφ (`src/Analysis.cc:5026-5028`) | ≠ (HEP17/HEM data-only) |
| HEM 2018 | `Hist/config/HemVeto.json` exists, not used in L3Residual ZllJet | via data hot map only | ≈ |

---

## 5. Muons (ZmmJet)

| Item | JS (`PickZllJet.json:12-20`, `PickZllJet.cpp:164-172,186-197`) | ZB (`src/Analysis.cc:4230-4290`) | |
|---|---|---|---|
| ID | `Muon_tightId == 1` | `Muon_tightId` (`:4248`) | = |
| Isolation | `Muon_pfRelIso04_all < 0.15` | `Muon_pfRelIso04_all < 0.15` (`:4237,4250`) | = |
| |η| | ≤ 2.3 | < 2.3 (`:4235`; `log_version.txt` Ver5 says 2.4 — code is 2.3) | = |
| pT | ≥ 20 (lead) / ≥ 20 (others), **after** Rochester | > 20 / > 20 (`:4233-4234,4246`), **before** Rochester | ≈ (edge effect only) |
| Impact parameters | |dxy| < 0.2, |dz| < 0.5 | none | ≠ small |
| Rochester files | `POG/MUO/roccor/RoccoR2016aUL/2016bUL/2017UL/2018UL.txt` (`Hist/config/ScaleMuon.json:3,20,37,54`) | `roccor.Run2.v5/RoccoR2016aUL.txt` (`BCDEF`), `RoccoR2016bUL.txt` (`FGH`), `RoccoR2017UL.txt`, `RoccoR2018UL.txt` (`src/Analysis.cc:118-142`); **directory absent from repo**, silently skipped | = files / ≠ availability |
| Rochester method | data `kScaleDT`; MC `kSpreadMC` if gen-dressed μ within ΔR < 0.2, else `kSmearMC(nL, u)` with event-seeded RNG (`ScaleMuonFunction.cpp:60-87`); pT only rescaled | data `kScaleDT` (`:4263`); MC **always** `kSmearMC(nL, rand())` (`:4265-4272`, empty gen loop); full 4-vector scaled (`:4277`) | ≠ |
| Multiplicity | 2 ≤ N(selected μ) ≤ 3 else no Z (`PickZllJet.cpp:262-265`) | 2 ≤ N(all selected μ+e) ≤ 3 **and** 2 ≤ N(selected-flavour) ≤ 3 (`:4884,4890`); one lepton of either flavour must have pT > `ptmin1` (`passedCut1`, `:4251,4362`) | ≈ |
| Muon SFs | ID×Iso×Trig per Z lepton on MC (§13) | none | ≠ (weights) |

## 6. Electrons (ZeeJet)

| Item | JS (`PickZllJet.json:2-11`, `PickZllJet.cpp:151-162`) | ZB (`src/Analysis.cc:4292-4363`) | |
|---|---|---|---|
| ID | `Electron_cutBased ≥ 4` (Fall17V2 tight) | `Electron_cutBased_Fall17_V1 == 4` (`:4296`; branch absent in v9) | ≠ |
| Isolation | in cutBased | `Electron_miniPFRelIso_all < 1.0` (`:4316,4329`, no-op) | ≈ |
| η | `|η + deltaEtaSC| ≤ 2.4`, gap 1.4442–1.566 vetoed | `|η| < 2.4` (`:4315,4328`), no gap veto, `Electron_deltaEtaSC` unused | ≠ |
| pT | 25/25 | 25/25 (`:4313-4314`) | = |
| dxy/dz | none | `dxy > 0.05, dz > 0.10` (EB) / `0.10, 0.20` (EE) rejected, **signed** (`:4299-4306`) | ≠ small |
| Scale/smearing | none for V9 (`Hist/cpp/ScaleElectron.cpp:58-61`) | none; NanoAOD `Electron_pt` as stored (`:4338`) | = |
| 4-vector | massive (`Electron_mass`) | massless `SetPtEtaPhiE(pt,η,φ,|p|)` (`:4350`) | ≈ |
| Electron SFs | ID×Reco×Trig from `POG/EGM` (files absent) | none | ≠ (weights) |

## 7. Z candidate

| Item | JS (`PickZllJet.json:21-29`, `PickZllJet.cpp:260-313`) | ZB (`src/Analysis.cc:4614-4636,4930`) | |
|---|---|---|---|
| Pairing | OS pairs from 2–3 selected leptons; pair minimising |m − 91.1876| among pairs with |Δm| ≤ 20, pT ≥ 15, |η(Z)| ≤ 1.3; exactly one tag (`RunL3ResidualZllJet.cpp:172`) | all ℓ⁺ℓ⁻ pairs; pair minimising |m − 91.1876| among pairs with pT ≥ 15 and |Δm| ≤ 20 (`:4615,4625-4627`) | = (except η) |
| Mass window | 71.19–111.19 | 71.19–111.19 | = |
| pT(Z) | ≥ 15 | ≥ 15 (`:4625,4930`) | = |
| |η(Z)| | ≤ 1.3 | none | ≠ |
| Gen Z (MC) | `GenDressedLepton` OS pair, pT ≥ 12, ΔR(gen Z, reco Z) < 0.2 (`PickZllJet.cpp:534-538`) | `GenPart` ±11/±13 with a mother check that compares pdgId to an index (`:4369`), same `getZboson` (`:4906-4907`) | ≈ (gen only) |

---

## 8. Jets and corrections

### 8.1 JEC

| Item | JS (`Hist/cpp/ScaleJet.cpp:101-178`) | ZB (`src/Analysis.cc:3872-3996,4453-4488`) | |
|---|---|---|---|
| Source | correctionlib `POG/JME/<year>_UL/jet_jerc_WithL2ResNoUnc.json.gz` (`Hist/cpp/ScaleJetLoader.cpp:21-23`) | txt files `src/CondFormats/JetMETObjects/data/*.txt`, `FactorizedJetCorrector` | ≈ |
| Tags | Summer19UL16APV_V7 (RunBCD / RunEF), Summer19UL16_V7 (RunFGH), **Summer19UL17_V5** (RunB…F), Summer19UL18_V5 (RunA…D), AK4PFchs | Summer19UL16APV_V7 (RunBCD / RunEF), Summer19UL16_V7 (RunFGH), **Summer19UL17_V6** (RunB…F), Summer19UL18_V5 (RunA…D), AK4PFchs; era from the dataset name (`:3853-3859`) | ≠ 2017 |
| Levels, MC | L1FastJet(area, η, pT, ρ) × L2Relative (× JER) (`:103,120`) | L1FastJet × L2Relative × L3Absolute × L2L3Residual(MC file = identity) × JER (`:3981-3986,4461-4476`) | = (identity files) |
| Levels, data | + L2Residual (Derivation) **or** + L2L3Residual (Closure) | + L3Absolute(=1) + L2L3Residual always | ≠ for derivation |
| Jets corrected | all (`Jet_pt`, `Jet_mass` overwritten, `:209-222`) | all in the ΔR-cleaned list (`:4939-4942`); jets removed by cleaning keep NanoAOD pT and never enter MET | ≈ |
| L1 for MET | L1FastJet on μ-subtracted raw pT (`:67,116`) | **L1RC** on raw pT, unsmeared (`:4480-4486`) | ≠ |

### 8.2 JER (MC)

| Item | JS (`Hist/cpp/ScaleJetFunction.cpp:258-398`) | ZB (`src/Analysis.cc:4490-4509`) | |
|---|---|---|---|
| Inputs | Summer20UL16APV_JRV3, Summer20UL16_JRV3, **Summer19UL17_JRV3**, Summer19UL18_JRV2 (AK4PFchs), correctionlib `jer_smear.json.gz` | Summer20UL16APV_JRV3, Summer20UL16_JRV3, **Summer19UL17_JRV2**, Summer19UL18_JRV2 (AK4PFchs txt, `:3989-3993`) | ≠ 2017 |
| Method | hybrid: scaling `1 + (SF−1)(pT−pT_gen)/pT` if `Jet_genJetIdx` match with ΔR < 0.2 and |Δpt| < 3σ·pT, else stochastic `N(0, σ√(SF²−1))`; σ at JES-corrected pT; seed hash(event, run, lumi) | **stochastic only** `1 + N(0, σ)·√(max(SF²−1, 0))`, clipped at 0; σ(pT_corr, η, ρ), SF(η); `mt19937(92837465)` | ≠ |
| Which jets | all | all (pT and mass) | = |
| In MET | yes (`ScaleJet.cpp:171`) | yes (`jet_corr` is smeared; `Jet_pt_corr_L1rc` is not, commit f6c535a) | = |

### 8.3 Jet selection, ID, cleaning

| Item | JS (`PickZllJet.cpp:350-480`, `PickJetId.cpp`) | ZB (`src/Analysis.cc:4937-4949,4575-4600,5018,5038,5050-5071`) | |
|---|---|---|---|
| Candidate jets | corrected pT ≥ 12; `Jet_muonIdx1/2 == −1` (Zee: `electronIdx1/2`); ΔR ≥ 0.4 to pT-selected leptons | all `nJet`; ΔR ≥ 0.3 to **all** selected μ and e (both flavours); then JEC(+JER); pT-order; `Jet_jetId ≥ 4` on every jet | ≠ |
| Probe (jet1) | highest-pT candidate; TightLepVeto (+ tight PU ID if pT < 50); `|η| ≤ 1.3` else event dropped | highest-pT ID'd jet with pT ≥ 12, `|η| ≤ 2.5` (`:4577-4578`), else dropped (`:5018`); veto map | ≠ (PU ID, η range) |
| jet2 (for α) | 2nd highest-pT candidate, pT ≥ 12, any η, **no ID** | next entry of the pT-ordered ID'd list (`getLeadingJetIndex(jetSelection, 1)`), any η (may be |η| > 2.5 and harder than jet1); α = 0 if pT2 < 15 | ≈ / ≠ (ID, floor) |
| Jetn (for MPFn) | Σ candidate jets with pT ≥ 12, idx-cleaned but **not** ΔR-cleaned, excluding jet1 (jet2 included) (`:458-480`) | `jets_all − jet1` with `jets_all` = Σ `jetSelection` jets with pT > 15 (`:5050,5065-5071`) — ΔR-cleaned, ID'd | ≠ |
| Jet ID semantics | v9 `jetId ≥ 6` = tight ∧ tightLepVeto; PU ID bit 0 (UL2016) / bit 2 (UL2017/18) for pT < 50 (`PickJetId.cpp:109-148`) | `jetId ≥ 4` = tightLepVeto bit (`:4570`); `Jet_puId` read, unused | ≈ for ID; ≠ PU ID |
| Spike / extra vetoes | none | none in this branch | = |

---

## 9. MET / Type-1 recipe

| Step | JS (`ScaleJet.cpp:60-215`, `ScaleMet.cpp:43-79`) | ZB (`src/Analysis.cc:4660-4758`) | |
|---|---|---|---|
| Seed | `RawMET` (PF) | `ChsMET` (raw CHS) for R_MPF (`:4664`); `MET_pt` for `R_MPFfromType1` (`:4666,4713`); `RawMET` for `R_MPFPF` (`:4667`) — the `hprof2D_*RMPF` profiles are filled with `R_MPFPF`, the `h_Zpt_RMPF*` TH2s with R_MPF | ≠ |
| Jet set | all jets with `ptRawMinusMuon ≥ 10 && ptFinal > 15 && |η| < 5.2 && EMF < 0.9`, no ID | `jetSelection` (ΔR ≥ 0.3 cleaned, tightLepVeto) with `pT_corr > 15` (`:4706`), any η, no EMF cut | ≠ |
| Subtracted term | `ptFinal − ptL1FastJet` on μ-subtracted raw pT (final incl. L2Rel, residual, JER) | `pT_corr − pT_L1RC` on raw pT (`:4712`) | ≠ |
| Lepton propagation | intended `p4CorrMet += p4RawTag − p4Tag`, no-op (`RunL3ResidualZllJet.cpp:175-176,224`) | none (block commented `:4720-4724`) | = (effectively) |
| Unclustered (MPFu) | `−(MET + Z + jet1 + Jetn)` (`Hist/cpp/MathHdm.cpp:58-118`) | `−MET − jets_all − Z` (`:5125`) | = formula, ≠ jet sets |

---

## 10. Event selection and cutflow order

JS (`RunL3ResidualZllJet.cpp:147-241`): HLT → golden JSON → (gen-vertex match, commented) → leptons (ID/iso/η/IP) → Rochester → pT cuts → exactly one Z (|Δm| ≤ 20, pT ≥ 15, |η| ≤ 1.3) → jets corrected → probe (idx+ΔR 0.4 cleaning, pT ≥ 12, TightLepVeto + PU ID, |η| ≤ 1.3) → |Δφ − π| < 0.44 → veto map on probe → α histograms → α < 1.0 → 0.3 < R_pT < 1.7 and 0.3 < R_MPF < 1.7 → fill; MC: gen Z matched, SFs.

ZB (`src/Analysis.cc:4790-5700`): pick-events list (`:4800`) → PU weight > 0 (MC) → HLT OR → MET filters (data, OR) → μ (pT > 20, |η| < 2.3, tight, iso) and e (pT > 25, |η| < 2.4, cutBased_V1 tight, IP) of both charges; Rochester on μ → 2 ≤ N(all ℓ) ≤ 3 and 2 ≤ N(flavour) ≤ 3 → Z (pT ≥ 15, |Δm| ≤ 20, closest to 91.1876) → jets: ΔR 0.3 clean vs all ℓ → JEC(+JER) → pT order → tightLepVeto → ≥ 1 jet → leading jet pT ≥ 12, |η| ≤ 2.5 → veto map → `|Δφ − π| < 0.34` → jet2, α (0 if pT2 < 15) → Type-1 MET, responses → **R_pT ≥ 0.5** → fill for α < 1.0 × |η| bins (0–1.3, 0–2.5) × PS-weight index.

Consequences: (i) probe |η| ≤ 1.3 bin is equivalent between the two once JS's |η(Z)| cut is removed; (ii) ZB jet2 and the MET jet set are ID'd, JS's are not; (iii) ZB cleans jets against electrons in the Zmm channel and vice versa; (iv) ZB's Δφ window is tighter (0.34 vs 0.44) and its response cut is one-sided (R_pT ≥ 0.5), JS's is two-sided on both R_pT and R_MPF.

---

## 11. Response mathematics and histogramming

| Quantity | JS (`Hist/cpp/MathHdm.cpp:58-118`) | ZB (`src/Analysis.cc:5121-5142`) | |
|---|---|---|---|
| R_pT | pT(probe)/pT(Z) | `leadingJet.Pt()/Zboson.Pt()` (`:5128`) | = |
| R_MPF | 1 + MET⃗·Z⃗/pT(Z)² (Type-1 from RawMET) | `1 + MET·(cosφ Zx + sinφ Zy)/pT(Z)²` (`:5131`, Type-1 from ChsMET) | = formula, ≠ MET |
| MPF1 | 1 − (Z⃗ + jet1⃗)·Z⃗/pT² | `R_MPFjet1 = −jet1⃗·Z⃗/pT²` (`:5133`, no "1 +") | ≈ (offset by 1) |
| MPFn | −Jetn⃗·Z⃗/pT² | `−jets_notLeadingJet⃗·Z⃗/pT²` (`:5134`) | = formula, ≠ jet set |
| MPFu | −(unclustered)·Z⃗/pT² | `−METuncl⃗·Z⃗/pT²` (`:5135`) | = formula |
| MPFnu | MPFn + 1.1·MPFu | none | — |
| MPFx | computed, not stored | none in this branch | — |
| Variants | — | `R_MPFfromType1` (NanoAOD `MET` re-corrected), `R_MPFPF` (RawMET Type-1) (`:5138-5142`); `JNPF = Σ cos Δφ(jet, MET)` (`:5147-5154`) | — |
| Gen-level (MC) | gen tag/probe via `GenDressedLepton`, GenJet ΔR < 0.2 pT ≥ 10 | `R_pTGen`, `R_MPFGen`, `R_GMPF`, `JESRpTGen = R_pT/R_pTGen`, `JESRMPFGen`; leading GenJet = nearest ΔR with **no** ΔR/Δpt cut (`:4998-5010,5160-5162,5261-5270`); flavour split by `Jet_partonFlavour` | ≈ |
| Storage | TProfile vs pT(Z) [15…1500] (`p1RespDbInTagPt`, `p1RespMpfInTagPt`, `p1RespMpf1/Mpfn/Mpfu/MpfnuInTagPt`); TProfile2D (η_probe, pT(Z)); TH1 R ∈ [0, 2] (50 bins) (`Hist/cpp/HistL3Residual.cpp:98-124,175-203`); α profiles binned in **probe pT** (`HistAlpha.cpp:112-158`) | TH2 pT(Z) [12, 15, …, 1500] (21 bins) × R ∈ [−3.99, 5.99] step 0.02 (`:218,275-276,518`); names `h_Zpt_RpT_alpha100_eta_00_13`, `h_Zpt_RMPF_alpha100_eta_00_13`, `…_eta_00_25`, `h_Zpt_RMPFjet1/RMPFjetn/RMPFuncl/RMPFfromType1/RMPFPF…` (`:1428-1436,1453-1459`); TH3 with μ; copies per PS weight in `analysis/PSWeight0..3/` | ≈ |
| ⟨R⟩ extraction | TProfile mean after the 0.3–1.7 window | `ProjectionY(ibin).GetMean()` per pT(Z) bin over [−3.99, 5.99] after R_pT ≥ 0.5; x = bin centre (`plot_v2.py:1229-1238`); graphs `ptchs_zmmjet_a100`, `mpfchs_zmmjet_a100` etc. in `figures/jet_response_<hist>.root` (`:1746-1771`) | ≠ |

---

## 12. Event weights

| Component | JS (`Hist/cpp/ScaleEvent.cpp:102-125`, `RunL3ResidualZllJet.cpp:247-267`) | ZB (`src/Analysis.cc:4805-4820`, `plot_v2.py:351-369`) | |
|---|---|---|---|
| Generator | genWeight/⟨genWeight⟩ | **none** | ≠ |
| L·σ/N | at fill, hard-coded lumi | at plotting, brilcalc lumi | ≈ |
| PU | correctionlib nominal | data/MC histogram ratio | ≈ |
| Lepton SF | ID×Iso×Trig (μ) / ID×Reco×Trig (e), MC | none | ≠ |
| L1 prefiring | 2018 only (`ScaleEvent.cpp:116`) | none | ≠ (both wrong in different ways) |
| PS weights | only for Isr/Fsr systematic runs | 4 alternative fills `PSWeight[i]·LHEWeight_originalXWGTUP` (`:4813-4820`), nominal unaffected | = |
| HEM / HLT / btag | 1 | — | = |

---

## 13. Per-year matrix of versioned inputs

| Input | 2016Pre | 2016Post | 2017 | 2018 |
|---|---|---|---|---|
| **JS** JEC data | Summer19UL16APV_RunBCD_V7 / RunEF_V7 | Summer19UL16_RunFGH_V7 | Summer19UL17_Run{B..F}_**V5** | Summer19UL18_Run{A..D}_V5 |
| **ZB** JEC data | same | same | Summer19UL17_Run{B..F}_**V6** | same |
| **JS** JEC MC | Summer19UL16APV_V7 | Summer19UL16_V7 | Summer19UL17_V5 | Summer19UL18_V5 |
| **ZB** JEC MC | Summer19UL16APV_V7 (+identity L3Abs/L2L3Res) | Summer19UL16_V7 | Summer19UL17_**V6** | Summer19UL18_V5 |
| **JS** JER | Summer20UL16APV_JRV3 | Summer20UL16_JRV3 | Summer19UL17_**JRV3** | Summer19UL18_JRV2 |
| **ZB** JER | Summer20UL16APV_JRV3 | Summer20UL16_JRV3 | Summer19UL17_**JRV2** | Summer19UL18_JRV2 |
| Rochester (both) | RoccoR2016aUL | RoccoR2016bUL | RoccoR2017UL | RoccoR2018UL (ZB: files not in repo) |
| **JS** PU | `Collisions16_UltraLegacy_goldenJSON` (preVFP json) | (postVFP json) | `Collisions17_UltraLegacy_goldenJSON` | `Collisions18_UltraLegacy_goldenJSON` |
| **ZB** PU | pileupCalc 69.2 mb per dataset / skim `Pileup_nTrueInt` | same | same | same |
| Golden JSON | JS Legacy2016 (applied); ZB per-era slices (not applied at HEAD) | same | UL2017 | Legacy2018 |
| **JS** MET filters | 7 (incl. EcalDeadCell, eeBadSc), data+MC | 7 | 8 (+ecalBadCalib) | 8 |
| **ZB** MET filters | skim 6 (incl. BadPFMuonDz) data+MC; analysis 6 OR-ed, data | same | skim 6; analysis 7 OR-ed | same |
| HLT Zmm | both `Mu17_Mu8_DZ` | same | JS `_DZ_Mass8`; ZB `_DZ` ∨ `Mu19_Mu9_DZ` ∨ `_DZ_Mass3p8` | same as 2017 |
| HLT Zee | JS DZ; ZB DZ ∨ non-DZ | same | non-DZ (JS) / DZ ∨ non-DZ (ZB) | same |
| **JS** veto map | Summer19UL16_V1 `jetvetomap_hot`, data+MC | same | Summer19UL17_V1 | Summer19UL18_V1 |
| **ZB** veto map | UL16 data `h2hot_ul16_plus_hbm2_hbp12_qie11`, MC `h2hot_mc` | same | UL17 data `…_plus_hep17_plus_hbpw89`, MC none | UL18 data `…_plus_hem1516_and_hbp2m1`, MC none |
| **JS** prefiring | none | none | none | `L1PreFiringWeight_Nom` |
| **ZB** prefiring | none | none | none | none |
| Lumi (JS, fb⁻¹) | 19.5 (Hist) | 16.8 | 41.5 | 59.8 |
| Lumi (ZB) | brilcalc per dataset from the golden JSON | | | |

---

## 14. Code-health findings relevant to the sync

### JERCSW
1. `Hist/POG/EGM/` is git-ignored and absent → ZeeJet Hist cannot run (`Hist/cpp/ScaleElectronLoader.cpp:58-61,89-95`).
2. `Hist/Inputs.py:6-9,25-34`: stage `Closure`, ZmmJet only. For the derivation sync switch to `Derivation` and enable ZeeJet.
3. `RunL3ResidualZllJet.cpp:175-176,224`: `p4RawTag == p4Tag`, so lepton corrections are not propagated to MET.
4. `ScaleEvent.cpp:116`: L1 prefiring weight applied for 2018 only (ECAL prefiring affects 2016/2017).
5. `Hist/config/ScaleMuon.json`: ID SF `NUM_TrkHighPtID_DEN_TrackerMuons` with a `tightId` selection; single-muon trigger SF multiplied for both muons under a dimuon path.
6. `Hist/config/RunL3ResidualZllJet.json`: `minPtJet2InAlpha`, `maxTagEta` read but unused (`.cpp:216` commented; η(Z) cut comes from `PickZllJet.json:26`).
7. `PickZllJet.cpp:458-480`: Jetn skips the ΔR(jet, ℓ) cleaning used for jet1/jet2.
8. `Hist/cpp/HistAlpha.cpp:112-158`: α-cut profiles are binned in probe pT, not pT(Z) — not directly comparable to ZB's `h_Zpt_*_alpha100`.
9. `Skim/input/SamplesNano_MapToLumiInFb.json:3-4`: 2016PreBv1 = 2016PreBv2 = 2.914 fb⁻¹ (unused by Hist, but wrong).
10. `Hist/cpp/PickJetId.cpp:138-139`: the function named "Loose" PU ID selects the Tight bit.

### ZbAnalysis (KITcomparison)
1. Golden JSON not applied (`multicrab.py:664-666` commented, `PSet.py:7` commented, no JSON code in `src/Analysis.cc`).
2. `src/Analysis.cc:4206-4216`: MET filters OR-ed instead of AND-ed; MC exempt at analysis level.
3. No `genWeight` in the nominal weight (`:4805`; `eventWeight = 1`, `:143-154`).
4. `:5341`: hard `R_pT ≥ 0.5` cut before all response histograms.
5. `:4265-4272`: Rochester MC gen-matching loop is empty → `kSmearMC` always; `roccor.Run2.v5/` not in repo → corrections silently off (`:136-142`).
6. `:4296`: `Electron_cutBased_Fall17_V1` (v7-era branch); `:4299-4306` signed IP cuts; `:4316` isolation no-op.
7. `:4490-4509`: stochastic-only JER for all MC jets, fixed seed shared across the whole job.
8. `:4664`: default R_MPF seeded from `ChsMET`, while `hprof2D_*RMPF` use the `RawMET`-based `R_MPFPF` (`:5727-5757`) — two inconsistent MPF definitions in one output.
9. `:4669` `verbose = true` and `:5220` unconditional `printSync` → every event printed three times; must be switched off for production.
10. `:248-251`: `bins_alpha` allocated with `nbins_alpha` entries but `nbins_alpha+1` written (one-past-the-end write).
11. `:4630`: `lm.push_back(leptMinus[i])` should be `[j]` (harmless, members unused).
12. `:4369`: gen-lepton "mother" check compares `pdgId` with `genPartIdxMother`.
13. `analyse.py:25`: `LEPTONFLAVOR = 11` hard-coded; `analyse.py:48-80` xsec table is dead code; `plot.py` (legacy) hard-codes a whitelist and α/η loops that no longer match the histograms — use `plot_v2.py`.
14. `NanoAOD_ZbAnalysisSkim.py:161`: `Flag_BadPFMuonDzFilter` required at skim, absent in the NanoAODv2 datasets listed in `multicrab.py`; `src/JetvetoMap.cc:13-18`: no MC map for 2017/2018.
15. `src/Analysis.cc:3853-3869`: JEC era derived from the multicrab directory and dataset names by regex; a `Run2016BCDEFGH` directory aborts.

---

## 15. Open questions

1. Which NanoAOD campaign are the ZB skims used for the KIT comparison (NanoAODv2 as in `multicrab.py`, or v9)? This decides `Electron_cutBased_Fall17_V1` vs `Electron_cutBased`, `Flag_BadPFMuonDzFilter`, and whether `Jet_jetId ≥ 4` and JS's `≥ 6` are the same WP.
2. Were the ZB skims produced with a `lumiMask`? If not, the data sample contains non-certified lumi sections while the lumi and PU profile assume the golden JSON.
3. Is the ZB comparison meant as closure (L2L3Residual on data) only? JS derivation needs L2Residual-only data in both.
4. MET: agree on one Type-1 recipe — seed (`RawMET` PF vs `ChsMET`), offset (L1FastJet on μ-subtracted raw vs L1RC on raw), jet set (all jets with EMF < 0.9 vs ID'd cleaned jets), and whether lepton corrections are propagated.
5. Is JS's |η(Z)| ≤ 1.3 intentional?
6. Δφ 0.44 vs 0.34 and the response window (0.3–1.7 on both R vs R_pT ≥ 0.5): which defines the baseline?
7. JER: hybrid (JS) vs stochastic-only (ZB, "KIT example"); Summer19UL17 JRV3 vs JRV2; JEC Summer19UL17 V5 vs V6.
8. Zmm 2017/2018 trigger: `_DZ_Mass8` (JS) vs the ZB OR including the plain `_DZ` path; recorded lumi of the OR must be checked (brilcalc) before comparing data yields.
9. Should genWeight be applied in ZB (aMC@NLO negative weights)?
10. Are the Rochester text files present on the machine running ZB?

---

## 16. Proposed common baseline (for discussion)

1. Inputs: JMENanoAODv9 (or plain UL NanoAODv9) CHS in both; DoubleMuon, DoubleEG/EGamma; DY amc@NLO only (drop tt̄ from the response plots or add it in both); golden JSON applied in both (data).
2. HLT: Zmm `Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ` (2016) / `_DZ_Mass8` (2017–18) or `_DZ_Mass3p8` — one path, same in both; Zee `Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ` (2016) / `_IsoVL` (2017–18); no trigger-object matching.
3. MET filters: JetMET UL list (goodVertices, globalSuperTightHalo2016, HBHENoise, HBHENoiseIso, EcalDeadCellTriggerPrimitive, BadPFMuon, BadPFMuonDz, eeBadSc, ecalBadCalib for 2017–18), AND-ed, data and MC.
4. Muons: tightId, pfRelIso04 < 0.15, |η| < 2.3, pT > 20/20; Rochester before the pT cut, data `kScaleDT`, MC `kSpreadMC` (gen-matched) else `kSmearMC`; dxy/dz in both or neither.
5. Electrons: `Electron_cutBased ≥ 4` (Fall17V2), |η_SC| < 2.4 with 1.4442–1.566 veto, pT > 25/25; no IP cuts or the same ones; no extra scale/smearing on v9.
6. Z: |m − 91.1876| < 20, pT > 15, closest-to-mZ OS pair, 2 ≤ N_ℓ ≤ 3, **no η(Z) cut**.
7. Jets: same JEC tags (decide Summer19UL17 V5 vs V6); data L2Residual only for derivation; JER hybrid on all jets with the same JR versions; cleaning ΔR ≥ 0.4 (plus `muonIdx/electronIdx == −1`) against the two Z leptons only; probe TightLepVeto, |η| < 1.3, pT > 12; PU ID off in both (or on in both); jet2 = 2nd cleaned jet with pT > 15 (α = 0 otherwise), no ID or ID in both.
8. Δφ: |Δφ − π| < 0.44; common α set {0.3, 1.0} (+ 0.1/0.2/0.5 optional); same response window (0.3–1.7 on R_pT and R_MPF, or none) in both.
9. MET: `RawMET` seed; Σ(pT^{L1L2L3(Res)(JER)} − pT^{L1FastJet}) on μ-subtracted raw pT for jets with pT_corr > 15, EMF < 0.9, |η| < 5.2, no jet ID (CMSSW Type-1 recipe); no lepton propagation (or in both).
10. Weights: genWeight and PU on in both; no lepton SFs / prefiring in the sync stage.
11. Histograms: TProfile (or TH2 + mean over the same window) of R_pT, R_MPF, MPF1, MPFn, MPFu vs pT(Z) in [15, 20, …, 1500], probe |η| < 1.3.
12. Turn off ZB's per-event printing (`verbose`, `printSync`) or gate it on a pick-events list for the event-by-event step.

---

## 17. What already agrees

Zmm 2016 HLT path; Zee 2017/18 effective path; both apply the trigger to MC; JEC tags for 2016/2018 and era splits; JER inputs for 2016/2018; Rochester files; Golden-JSON certifications (files); muon ID/iso/|η|/pT thresholds; electron pT thresholds and tight WP (different ID version); Z mass reference 91.1876, window ±20, pT(Z) ≥ 15, closest-pair choice; DY amc@NLO sample and σ = 6077.22 pb; R_pT and R_MPF formulae; pT(Z) bin edges ≥ 15; α < 1.0 as the only event-level α requirement; JER applied to all MC jets and propagated into MET in both; PU reweighting on in both; jet veto map applied to the leading jet only in both.

## 18. Relation to the earlier comparison (`sync_samiPuppi_raviChs.md`, ZB `master` d2b5713)

The KITcomparison branch (2021) differs from the 2026 `master` in points that were listed as differences there and are **not** differences here: mZ reference 91.1876 (not 90), pT(Z) ≥ 15 (not 12), lepton pT 20/20 and 25/25 (not 20/10, 25/15), no trigger-object matching, JER on all jets (not first 3), Rochester `kSmearMC` (not `kScaleMC×kExtra` with a 26 GeV floor), PU reweighting on (not off), CHS JEC txt files present in the repo, `RawMET`/`ChsMET` (not `RawPuppiMET`), no spike veto. New relative to that document: Δφ 0.34, hard R_pT ≥ 0.5, `ChsMET` seed with L1RC offset, ID'd MET jet set, stochastic-only JER, unapplied golden JSON, OR-ed MET filters, no genWeight, unpinned NanoAOD version.
