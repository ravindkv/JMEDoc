# JERCSW ↔ NanoAnalysis synchronisation: Z(→μμ/ee)+jet residual JEC, Run 2 UL

Scope: ZmmJet and ZeeJet channels, years 2016Pre (APV/HIPM), 2016Post, 2017, 2018.
Compared code states:

| Framework | Repo | HEAD |
|---|---|---|
| JERCSW | `gitlab.cern.ch/cms-analysis/jme/jerc-derivation/JERCSW` | `28b832f` "synchronising with Sami/KIT" |
| NanoAnalysis | `gitlab.cern.ch/slehti/NanoAnalysis` | `29fb0be` (merge of origin/master) |

Conventions: **JS** = JERCSW (`Skim/`, `Hist/`), **NA** = NanoAnalysis (`NanoAODSkim/`, `NanoAODAnalysis/ZbAnalysis/`, `NanoAODAnalysis/Framework/`). Paths are relative to the two package roots. "≠" marks a difference that changes the selected events or the response; "≈" marks a difference that should be numerically negligible or is a pure implementation detail.

---

## 0. Executive summary — differences that will move the response

Ordered by expected impact on the derived L3Residual.

| # | Item | JERCSW | NanoAnalysis | Impact |
|---|---|---|---|---|
| 1 | **Z pseudorapidity cut** | `\|η(Z)\| ≤ 1.3` (`Hist/config/PickZllJet.json:26`, applied in `PickZllJet.cpp:305`) | none | Large acceptance change; NA has no such cut. Confirm whether this is intended (it is not a standard L3Res Z+jet cut). |
| 2 | **Sub-leading lepton pT** | μ: 20/20 GeV, e: 25/25 GeV (`PickZllJet.json:3-4,13-14`) | μ: 20/10, e: 25/15 (`ZbSelection.py:56-63`) | Different Z acceptance at low pT(Z). |
| 3 | **MET used for MPF** | Type-1 from **RawMET** (PF), μ-subtracted jets, EMF<0.9, raw(1−μ)≥10 & corr>15 (`ScaleMet.cpp:43-79`, `ScaleJet.cpp:188-192`) | Type-1 from **ChsMET**, jets corr-pT>15 only, no μ-subtraction, no EMF cut, L1RC reference (`JetCorrections.py:435-461`) | Different MET definition → MPF, MPFn, MPFu differ. |
| 4 | **Zee HLT logic** | 2016: `Ele23_Ele12_…_IsoVL_DZ`; 2017/18: `Ele23_Ele12_…_IsoVL` (non-DZ) (`Hist/config/HltZeeJet.json`) | `IsoVL && IsoVL_DZ` for all years (`ZbSelection.py:14-16`) | 2017/18 Zee data differ (DZ vs non-DZ). |
| 5 | **Electron ID** | cutBased ≥ 4 (tight), EB/EE gap veto, \|η_SC\|≤2.4 | *none* — "leptonSelection for electrons not implemented" (`ZbSelection.py:44-51`) | NA Zee is not usable as-is. |
| 6 | **Response window** | 0.3 < R_bal < 1.7 **and** 0.3 < R_MPF < 1.7 required for final histos (`RunL3ResidualZllJet.json:20-21`, `RunL3ResidualZllJet.cpp:236-241`) | none (TH2 y range −3.99…6.01) | Truncation bias on means. |
| 7 | **α definition** | jet2 = 2nd jet with pT≥12 (no ID, any η); hard cut α<1.0; no pT floor (the `minPtJet2InAlpha=30` logic is commented out, `RunL3ResidualZllJet.cpp:214-216`) | jet2 = 2nd jet (any pT, any η); α := 0 if pT(jet2)<15 (`ZbHistograms.py:289-292`); no hard cut, α<0.3 / α<1.0 histograms | Different α-binned samples; NA uses α<0.3, JS α<0.1/0.2/0.5/1.0. |
| 8 | **Z mass window centre** | \|m − 91.1876\| ≤ 20 | \|m − 90\| ≤ 20 (`ZbSelection.py:71,93`) | Window shifted by 1.19 GeV. |
| 9 | **Lepton-jet cleaning** | `Jet_muonIdx1/2 == −1` (or electronIdx) **and** ΔR(jet,ℓ) ≥ 0.4 (`PickZllJet.cpp:379-420`) | ΔR(jet,μ) < 0.3 removed; **no electron cleaning** (`CommonSelection.py:21-34,45-58`) | Different jet collection near leptons; affects jet1/jet2/MPFn. |
| 10 | **Muon dxy/dz** | \|dxy\|<0.2, \|dz\|<0.5 | none | Small. |
| 11 | **PU jet ID on probe** | tight-WP PU ID for pT<50 (`Jet_puId` bit 0 in UL2016, bit 2 in UL2017/18; `PickJetId.cpp:109-140`) | none | Low pT(Z) bins. |
| 12 | **Lepton SFs / trigger SF / L1-prefiring** | ID×Iso×Trig per lepton, L1 prefiring (see bugs §13) | none | Normalisation only (ratio-insensitive) but affects MC shapes vs data. |
| 13 | **MC sample** | amc@NLO DYJetsToLL (+ Herwig7 alt.), σ = 6077.22 pb | madgraphMLM **and** amc@NLO **and** TTJets all processed and merged into "MC" by `post_process.py:158`; σ = 5765.4 pb | Possible double counting; different σ. |
| 14 | **JER version / inputs** | 2017: Summer19UL17_**JRV3**; σ_JER evaluated at JES-corrected pT | 2017: Summer19UL17_**JRV2**; σ_JER evaluated at **raw** pT (`JetCorrections.py:474-478`) | Small; MC only. |
| 14b | **Rochester 2016Pre** | `RoccoR2016aUL.txt` | `dataset.run` never contains "APV" → `RoccoR2016bUL.txt` is used for preVFP too (`RochesterCorrections.py:17-20`, `multicrabdatasets.py:259-270`) | 2016Pre muon scale. |
| 15 | **MET filters** | no `BadPFMuonDzFilter`; 2016 has `EcalDeadCellTriggerPrimitiveFilter` | 2016 lacks `EcalDeadCell…`; 2017/18 have `BadPFMuonDzFilter` | Small. |

Code-health notes that matter for the sync (details in §16):
- JS as checked out: `Hist/Inputs.py:6-9,25-34` runs the **`Closure`** stage (data jets get L2L3Residual, not L2Residual) and enables **ZmmJet only**; `Hist/POG/EGM/` (electron SF files) is absent, so the ZeeJet Hist step cannot run without adding them.
- NA's `ZbAnalysis/analysis.py` (coffea) imports Framework modules that were since refactored to RDataFrame (`METCleaning`, `PileupWeight`, `LumiMask`, `JetCorrections`): as committed the coffea path will not run. `analysis_RDataFrame.py` is a 140-line stub. The physics comparison below uses the *coffea logic* as the definition of the NA selection; **confirm which code produced the NA results being compared.**
- JS: the "replace PF tag with reco tag" MET correction is a no-op (`RunL3ResidualZllJet.cpp:175-176,224`: `p4RawTag` is assigned *after* Rochester was already written into `Muon_pt`).
- JS: L1-prefiring weight applied for **2018 only** (`ScaleEvent.cpp:116`); should be 2016/2017 (ECAL) — 2018 has no ECAL prefiring weight.
- JS: muon ID SF histogram is `NUM_TrkHighPtID_DEN_TrackerMuons` while the selection uses `Muon_tightId` (`Hist/config/ScaleMuon.json`); trigger SF is the *single-muon* IsoMu24/27 SF applied per lepton although the dimuon path is used.
- NA: `keep_and_drop_ZbAnalysis.txt` keeps only `HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8` → the 2016 dimuon path `…_DZ` (no `_Mass8`) is dropped from skims made with branch selection; `triggerSelection` then returns an all-false mask (`ZbSelection.py:19-25`).
- NA: MC yield normalisation uses N_events from the skim counter while the event weight carries sign(genWeight) (`tools/plotting.py:453-471`, `analysis.py:152`) → for aMC@NLO the MC yield is low by ⟨sign⟩ = (N₊−N₋)/N. Irrelevant for response means, relevant for any data/MC yield comparison. Also the task names `DYJetsToLL_M_50_LO/_NLO/_herwig7` have no entry in `tools/crosssection.py` (only `DYJetsToLL_M_50`, `…_amcatnloFXFX`, `…_madgraphMLM`).
- NA: `JetvetoMap` silently falls back to "Not using jetvetomaps" if the private `hotjets-*.root` files are absent (`JetvetoMap.py:42-55`); JEC/JR text databases are git submodules not checked out here.

---

## 1. Samples

### 1.1 Data — primary datasets (UL2016 MiniAODv2 / UL2017 MiniAODv2 / UL2018 MiniAODv2, **JMENanoAODv9**)

Both frameworks use the JME-custom NanoAODv9. DAS names agree except for the `-vN` suffix in a few 2016Pre entries.

| Year / Era | JS (`Skim/input/SamplesNano_<year>_Data.json`) | NA (`NanoAODSkim/python/datasets_ZbAnalysis.py`) | Note |
|---|---|---|---|
| 2016Pre B-ver1 | DoubleMuon/DoubleEG `Run2016B-ver1_HIPM…-v2` (μ), `-v2` (e) | *commented out* (L385, L392) | ≈ JS includes ver1 (tiny). Lumi map gives Bv1 = Bv2 = 2.914 fb⁻¹ (`SamplesNano_MapToLumiInFb.json:3-4`) — looks like a placeholder; verify. |
| 2016Pre B-ver2 | `…JMENanoAODv9-v2` (μ), `-v1` (e) | `-v1` (μ), `-v1` (e) | ≈ check the μ suffix |
| 2016Pre C, D, E | `-v2` (μ, e) | `-v1` (μ, e) | ≈ check suffixes — different re-processing versions |
| 2016Pre F (HIPM) | `Run2016F-HIPM…-v2` | `Run2016F-HIPM…-v2`, JSON `…Run2016F_HIP.txt` (277932-278800) | = |
| 2016Post F, G, H | `Run2016F-UL2016…-v2`, `G -v1`, `H -v1` | same | = |
| 2017 B-F | DoubleMuon / DoubleEG `-v1` | same | = |
| 2018 A-D | DoubleMuon / EGamma `-v1` | same; 2018D split into D1/D2/D3 by JSON | = |

Neither uses SingleMuon/SingleElectron for Z+jet (both have them listed/commented).

Luminosity (fb⁻¹):
- JS: per-year `getLumiPerYear()` 19.5 / 16.8 / 41.5 / 59.8 (`Hist/cpp/GlobalFlag.cpp:443-453`) used for MC normalisation; per-era values in `SamplesNano_MapToLumiInFb.json` (2016Pre: Bv1 2.914, Bv2 2.914, C 2.621, D 4.286, E 4.065, F 2.718; 2016Post: F 0.418, G 7.653, H 8.74; 2017: B 4.823, C 9.664, D 4.252, E 9.278, F 13.54; 2018: A 14.0, B 7.1, C 6.94, D 31.93).
- NA: per-dataset `lumi.json` produced by `NanoAODSkim/scripts/lumicalc.py` (brilcalc with `--normtag normtag_BRIL.json`, `lumicalc.py:12,19-44`; `normtag_PHYSICS` commented out) over the full assigned golden JSON, read in `multicrabdatasets.loadLuminosity` (`multicrabdatasets.py:444-453`); MC normalised to the summed data lumi at post-processing (`tools/plotting.py:632-637`).

### 1.2 MC

| | JS | NA |
|---|---|---|
| DY samples | `DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8` (key `DYJetsMgNloPy8`) and `DYJetsToLL_M-50_TuneCH3_13TeV-madgraphMLM-herwig7` (`DYJetsMgMlmHg7`), Summer20UL*JMENano (`Skim/input/SamplesNano_<year>_MC.json`) | `DYJetsToLL_M_50_LO` (madgraphMLM-pythia8), `DYJetsToLL_M_50_NLO` (amcatnloFXFX), `DYJetsToLL_M_50_herwig7`, `TTJets_…amcatnloFXFX` (`datasets_ZbAnalysis.py:343-346, 370-373, 406-409, 424-427`) |
| Sample actually used for Zmm | Nominal: `DYJetsMgNloPy8` | `blacklist=["DYJetsToLL_M_50_herwig7"]` (`analysis.py:297`) → **LO + NLO + TTJets** are all processed; `post_process.py:158` merges every non-Data dataset into one "MC" |
| Cross section | 6077.22 pb for both DY samples (`SamplesNano_MapToXsecInPb.json:2-3`) | `DYJetsToLL_M_50*` → 1921.8×3 = **5765.4 pb** NNLO (`tools/crosssection.py:504-529`); TTJets 831.76 pb (`:286-291`). No entry for the actual task names `…_LO/_NLO/_herwig7` |
| Normalisation | w = genWeight/⟨genWeight⟩ × 1000·L[fb⁻¹]·σ[pb]/N_DAS, with N_DAS the DAS event count of the dataset (`Skim/input/getNanoFiles.py`, `SkimFile.cpp:116`) and ⟨genWeight⟩ = Σ genEventSumw/Σ genEventCount from the `Runs` tree, cached in `Hist/config/RunsTree.json` (≈16995 for DY NLO) (`ScaleEvent.cpp:36,112-113`, `RunsTree.cpp:74-79`) | w = sign(genWeight) × PU (`analysis.py:152-156`); scaled to σ·L/N_skim in `post_process.py` (`normalizeToLumi`, `tools/plotting.py:453-471`) with N_skim = raw skim event count ("Skim: All events"), **not** Σ sign(genWeight) |

≠ Action: agree on one DY sample (NLO recommended, both have it) and one σ; check NA "MC" merge does not sum LO+NLO.

---

## 2. Skim-level selection

| | JS (`Skim/`) | NA (`NanoAODSkim/`) |
|---|---|---|
| Tool | RDataFrame snapshot, one job per (era, PD) (`Skim/cpp/RunChannel.cpp`) | nanoAOD-tools PostProcessor + CRAB (`test/NanoAOD_ZbAnalysisSkim.py`) |
| Event filter | `(AND of MET filters) && (OR of channel HLT paths)` (`RunChannel.cpp:46-62`); missing filter → true, missing trigger → false | OR of a long list of dimuon/dielectron/**single-lepton and prescaled** paths (`NanoAOD_ZbAnalysisSkim.py:99-168`: incl. `HLT_Mu17`, `HLT_Mu19`, `HLT_IsoMu24_eta2p1`, `HLT_Ele17_Ele12_*`, `HLT_HIMu17`, …). MET filters computed but **not applied** (`:186-187`). |
| Golden JSON | not at skim; in Hist | CRAB `lumiMask` per era (`datasets_ZbAnalysis.py`) |
| Branches kept | curated list: `ReadConfigCommon.json` (event, PV, rho, L1PreFiring, jets, MET, PSWeight, LHE_HT, Pileup, GenJet, GenPart) + channel `ReadConfigZmmJet.json` / `ReadConfigZeeJet.json` (Muon_*/Electron_*, GenDressedLepton_*, HLT paths) | `keep *` minus FatJet/Photon/Tau/SubJet/L1/HLT*, plus `keepmatch HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8`, `keepmatch HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL` (`keep_and_drop_ZbAnalysis.txt`) |
| Counters | `hEventsPerJobFromNano` (N_nano per job) | `configInfo/SkimCounter`, `pileup` (Pileup_nTrueInt) histogram |

≈ Skim differences do not matter once the analysis-level HLT/filters are applied, **except** the NA branch selection drops the 2016 `…_DZ` (non-Mass8) muon path (see §0).

---

## 3. HLT

| Year | Channel | JS (`Hist/config/HltZmmJet.json`, `HltZeeJet.json`; `ConfigHlt.cpp:20-27` maps 2016Pre/Post → "2016") | NA (`ZbSelection.py:12-25`) |
|---|---|---|---|
| 2016 | Zmm | `HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ` | `HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ` (if branch exists) |
| 2017, 2018 | Zmm | `HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8` | same |
| 2016 | Zee | `HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ` | `IsoVL && IsoVL_DZ` (≡ DZ) |
| 2017, 2018 | Zee | `HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL` | `IsoVL && IsoVL_DZ` (≡ DZ) |

- Logic: JS OR over the list (`PickHltOr.cpp`); NA single-path (or AND for e). Neither does offline–online matching. No prescale handling in either.
- Trigger SF: JS multiplies per-lepton trigger SF (`ScaleMuonFunction.cpp:180-184`, `ScaleElectronFunction.cpp:155-159`) from single-lepton histograms (`NUM_IsoMu24_or_IsoTkMu24…`, `NUM_IsoMu27…`, `NUM_IsoMu24…`; `egammaEffi.txt_TrigSFTightID_<year>.root`); NA none.

≠ Zee 2017/2018 path. ≠ trigger SF treatment (JS's is inconsistent with the dimuon path).

---

## 4. MET filters

| Year | JS (`Skim/config/ReadConfigCommon.json:143-172`, applied at skim) | NA (`Framework/…/METCleaning.py:10-29`, applied in analysis) |
|---|---|---|
| 2016 | goodVertices, globalSuperTightHalo2016Filter, HBHENoiseFilter, HBHENoiseIsoFilter, **EcalDeadCellTriggerPrimitiveFilter**, BadPFMuonFilter, eeBadScFilter | goodVertices, globalSuperTightHalo2016Filter, HBHENoiseFilter, HBHENoiseIsoFilter, BadPFMuonFilter, eeBadScFilter |
| 2017, 2018 | above + ecalBadCalibFilter | goodVertices, globalSuperTightHalo2016Filter, HBHENoiseFilter, HBHENoiseIsoFilter, EcalDeadCellTriggerPrimitiveFilter, BadPFMuonFilter, **BadPFMuonDzFilter**, eeBadScFilter, ecalBadCalibFilter |

Both apply to data and MC. JetMET UL recommendation is the NA 2017/18 list, with `EcalDeadCellTriggerPrimitiveFilter` and `BadPFMuonDzFilter` also in 2016 (no `ecalBadCalibFilter` in 2016). ≠ Neither is fully compliant: JS lacks `BadPFMuonDzFilter` (all years); NA lacks `EcalDeadCellTriggerPrimitiveFilter` and `BadPFMuonDzFilter` in 2016.

---

## 5. Golden JSON

| | JS | NA |
|---|---|---|
| Files | full-year: `Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt`, `Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt`, `Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt` (`Hist/config/PickEvent.json`) | per-era `Cert_*_Run20XXY.txt` in `NanoAODSkim/data/` (e.g. 2016F split HIP / HIPfixed; 2018D split D1/D2/D3) |
| Where | Hist, data only (`PickEvent.cpp:100-127`) | CRAB lumiMask at skim + `LumiMask` in analysis (`analysis.py:160-161`) |

= Equivalent (the per-era datasets themselves bound the run ranges).

---

## 6. Pileup reweighting

| | JS | NA |
|---|---|---|
| Method | correctionlib `POG/LUM/<year>_UL/puWeights.json`, key `Collisions1X_UltraLegacy_goldenJSON`, evaluated on `Pileup_nTrueInt`, "nominal" (`ScaleEvent.cpp:79-100`, `ScaleEvent.json`) | data profile from `pileupCalc` (min-bias σ = 69.2 mb, `NanoAODSkim/scripts/pileup.py:214`) per dataset → summed; MC profile = the sample's own `Pileup_nTrueInt` skim histogram; ratio of area-normalised histograms, 100 bins 0–100 (`PileupWeight.py:14-33`, `analysis.py:76-79,155`) |
| Systematics | up/down available in JSON, not used for Zll | PU up/down (`pileup.py:172-180`) produced, not used in analysis |

≈ Same min-bias σ and golden JSON; the MC denominator differs (central mix profile vs actual sample profile). Small but not zero.

---

## 7. Muon selection (ZmmJet)

| Cut | JS (`Hist/config/PickZllJet.json`, `PickZllJet.cpp:164-172,178-200`) | NA (`ZbSelection.py:30-42,55-59,66-67`) |
|---|---|---|
| pT preselection | — | pT > 8 (before Rochester) |
| \|η\| | ≤ 2.3 (preselection) | < 2.3 (only in `leptonPtCut`, on the Z leptons) |
| ID | `Muon_tightId == 1` | `tightId` |
| Isolation | `pfRelIso04_all < 0.15` | `pfRelIso04_all < 0.15` |
| IP | \|dxy\| < 0.2, \|dz\| < 0.5 | **none** |
| pT lead / sublead | ≥ 20 / **≥ 20** (leading = highest-pT preselected muon) | > 20 / **> 10** (counted among the two Z leptons) |
| Multiplicity | 2 ≤ N(selected, after pT cuts) ≤ 3 → else veto (`pickRecoZ:260-265`) | 2 ≤ N(pT>8,tight,iso) ≤ 3 and \|Σ charge\| ≤ 1 |
| Charge | Z pair strictly opposite sign | pair charge == 0 (from combinations) |
| Electron veto in Zmm | none | none |
| Rochester files | `RoccoR2016aUL.txt` (Pre), `RoccoR2016bUL.txt` (Post), `RoccoR2017UL.txt`, `RoccoR2018UL.txt` (`ScaleMuon.json`) | same files listed (`RochesterCorrections.py:17-24`, roccor.Run2.v5), **but** the `'APV' in run` test never fires (`run` = e.g. "2016BCDEF" from `multicrabdatasets.getRun`) → preVFP uses `RoccoR2016bUL.txt` |
| Rochester data | `kScaleDT(Q,pt,eta,phi)` | `kScaleDT` |
| Rochester MC | gen-matched (ΔR<0.2 to `GenDressedLepton`, \|pdgId\|=13) → `kSpreadMC(genPt)`; else `kSmearMC(nTrackerLayers, u)` with deterministic seed `event+run+lumi` (`ScaleMuonFunction.cpp:60-87`) | `Muon.matched_gen` (via `Muon_genPartIdx` → `GenPart`) → `kSpreadMC`; else `kSmearMC` with `np.random.rand` (non-reproducible) (`RochesterCorrections.py:47-72`) |
| Order | preselect → Rochester → pT cuts → Z | preselect (pT>8) → Rochester → Z → pT cuts |
| SFs (MC) | ID × Iso × Trig per Z lepton: `NUM_TrkHighPtID_DEN_TrackerMuons_abseta_pt` (**not TightID**), `NUM_TightRelIso_DEN_TightIDandIPCut_abseta_pt`, single-μ trigger SF (`ScaleMuon.json`; `ScaleMuonFunction.cpp:166-200`) | none |

≠ sublead pT, dxy/dz, gen-matching definition (dressed vs bare GenPart → different genPt for kSpreadMC), SFs. ≈ ordering, charge logic.

---

## 8. Electron selection (ZeeJet)

| Cut | JS (`PickZllJet.json:2-11`, `PickZllJet.cpp:151-162`) | NA (`ZbSelection.py:44-51,60-63`) |
|---|---|---|
| \|η_SC\| (= η + `deltaEtaSC`) | ≤ 2.4, veto 1.4442 < \|η_SC\| < 1.566 | \|η\| < 2.4 (detector η, no gap veto) |
| ID | `Electron_cutBased ≥ 4` (tight) | **none** |
| Isolation | in cutBased | none |
| pT lead / sublead | ≥ 25 / **≥ 25** | > 25 / **> 15** |
| Multiplicity | 2 ≤ N ≤ 3 | N == 2 (`ak.num == 2` and ≤3), \|Σq\| ≤ 1 |
| Scale & smearing | NanoAODv9: none extra (`Electron_pt` already corrected; `ScaleElectron.cpp:59-61` applies `eCorr` only for NanoV15) | none |
| SFs (MC) | ID (Tight) × Reco (ptAbove20) × Trig, evaluated at (η_SC, pT) from EGM `egammaEffi*.root` (`ScaleElectronLoader.json`, `ScaleElectronFunction.cpp:139-175`) | none |
| Muon veto in Zee | none | none |

≠ NA Zee has no electron ID — must be implemented before any Zee comparison.

---

## 9. Z candidate

| | JS (`PickZllJet.json:21-29`, `PickZllJet.cpp:245-327`) | NA (`ZbSelection.py:70-95`) |
|---|---|---|
| Pairing | all OS pairs of pT-selected leptons; choose min \|m − m_Z\| | all pairs with total charge 0; choose min \|m − m_Z\| |
| m_Z | 91.1876 | **90** |
| Window | ≤ 20 GeV → [71.19, 111.19] | ≤ 20 GeV → [70, 110] |
| pT(Z) | ≥ 15 | ≥ 15 |
| **\|η(Z)\|** | **≤ 1.3** | none |
| Gen Z (MC) | OS `GenDressedLepton` pair of the channel flavour, pT ≥ 12, ΔR(genZ, recoZ) < 0.2 (`pickGenZ:492-556`) | not built |

≠ η(Z) cut and mass centre.

---

## 10. Jets and corrections

### 10.1 Collection, JEC, JER

Both: AK4 PF CHS for Run 2.

| | JS (`Hist/config/ScaleJetLoaderSummer19ULNoUncAK4Chs.json`, `ScaleJet.cpp`) | NA coffea (`Framework/…/JetCorrections.py`) | NA RDF C++ (`Framework/…/include/JetCorrections.cpp`, `data/JercFileAndTagNamesAK4.json`) |
|---|---|---|---|
| Source | private `POG/JME/<year>_UL/jet_jerc_WithL2ResNoUnc.json.gz` (correctionlib) | JECDatabase text files | cvmfs `cat/metadata/JME/Run2-<year>-UL-NanoAODv9/latest/jet_jerc.json.gz` |
| 2016Pre | Summer19UL16APV_V7 (MC), RunBCD/RunEF_V7 (data) | Summer19UL16APV_V7 (B-D: RunBCD, E-F: RunEF) | Summer19UL16APV_V7 |
| 2016Post | Summer19UL16_V7, RunFGH_V7 | **F: Summer19UL16_RunFGH_V7; G,H: Summer20UL16_RunGH_V1; MC: Summer20UL16_V1** | Summer19UL16_V7 |
| 2017 | Summer19UL17_V5 (Run B–F) | Summer19UL17_**V6** | Summer19UL17_V5 |
| 2018 | Summer19UL18_V5 (Run A–D) | Summer19UL18_V5 | Summer19UL18_V5 |
| Levels (MC) | L1FastJet → L2Relative; L3Absolute name loaded but never evaluated (`GlobalFlag.cpp:230-246`, `ScaleJet.cpp:102-161`) | L1FastJet, L2Relative, L3Absolute, L2L3Residual (MC residual = 1) | L1FastJet, L2Relative |
| Levels (data) | + **L2Residual** in `Derivation` mode, + L2L3Residual in `Closure` mode — **current `Hist/Inputs.py` = Closure** | + L2L3Residual | + L2L3Residual |
| JER (MC) | Summer20UL16APV_JRV3 / Summer20UL16_JRV3 / Summer19UL17_**JRV3** / Summer19UL18_JRV2; hybrid via correctionlib `JERSmear` (`POG/JME/jer_smear.json.gz`), match ΔR<0.2 & \|Δpt\|<3σ·pt, hash seed (`ScaleJetFunction.cpp:258-398`) | Summer20UL16APV_JRV3 / Summer20UL16_JRV3 / Summer19UL17_JRV2 / Summer19UL18_JRV2; `smearing()` (`:467-493`) — see §16 | same tags as coffea; hybrid, ΔR<0.2 & 3σ, deterministic `normal_from_seed` (`:609-679`) |
| Jets corrected | all jets | all jets | only jets with NanoAOD pT ≥ 15 and \|η\| ≤ 5.2 (`collectNonOverlappingAK4Jets:1090-1113`) |
| Data era resolution | era token in the job name (`GlobalFlag.cpp:102-121`) | one `run` string per multicrab (`multicrabdatasets.getRun`, first matching directory) → era-correct data JEC only when one era is processed per run; `getYear` adds "APV" only for a name containing `Run2016BCDEF` | `Run20XX<letter>` regex on the dataset name (`rdf_backend/jet_corrections.py:148-152`) |
| pT ordering after JEC | jet1/jet2 chosen by corrected pT (`pickRecoJets:422-427`) | `argsort` by corrected pT (`:423`) | — |

≠ 2016Post/2017 JEC tag versions in the coffea table; ≠ 2017 JER version; ≈ everything else if NA runs with the RDF C++ path.

### 10.2 Jet ID, veto maps, cleaning, thresholds

| | JS | NA |
|---|---|---|
| Jet ID (probe) | TightLepVeto = `Jet_jetId ≥ 6` **and** tight-WP PU-ID for pT<50: `Jet_puId` bit 0 (UL2016) / bit 2 (UL2017-18), per the bit flip documented in cms-talk 37786 (`PickJetId.cpp:107-148`) | leading jet `jetId ≥ 4` (≡ 6 = TightLepVeto in NanoAODv9) (`ZbSelection.py:98-102`, applied at `analysis.py:202`); no PU ID |
| Jet ID (other jets) | none for jet2 / Σjets | none |
| Lepton cleaning | jet dropped if `Jet_muonIdx1 ≠ −1` or `Jet_muonIdx2 ≠ −1` (e: `electronIdx1/2`) **or** ΔR(jet, any selected lepton) < 0.4 (`PickZllJet.cpp:379-420`) | jet dropped if ΔR(jet, any pT>8 tight-iso muon) < 0.3 (`CommonSelection.py:45-58`); electrons: **not cleaned** (commented, `:25-26`) |
| Probe (jet1) | highest-pT surviving jet with pT ≥ 12; then require TightLepVeto and \|η\| ≤ 1.3 (L3Residual mode) (`:443-453`) | highest-pT jet with pT > 12 and \|η\| < 5 (`analysis.py:189-193`); η restriction only via histogram categories `eta_00_13` (`ZbHistograms.py:39-40`) |
| Jet veto map | correctionlib `jetvetomaps.json.gz`, `Summer19UL16_V1` / `Summer19UL17_V1` / `Summer19UL18_V1`, key `jetvetomap_hot`, applied to **probe only**, data & MC (`PickEvent.cpp:170-195`, `PickEvent.json`) | coffea: private `hotjets-UL16.root` (`h2hot_ul16_plus_hbm2_hbp12_qie11` data / `h2hot_mc` MC), `hotjets-UL17_v2.root` (`h2hot_ul17_plus_hep17_plus_hbpw89`, data only), `hotjets-UL18.root` (`h2hot_ul18_plus_hem1516_and_hbp2m1`, data only), leading jet only (`JetvetoMap.py`). RDF C++: same correctionlib tags as JS but **event veto if any jet** (pT>15, jetId≥6, EMF<0.9) is in the map (`JetCorrections.cpp:1052-1083`, `JvmFileAndTagNames.json`) |
| HEM 15/16 (2018) | `HemVeto` class exists but not used in `RunL3ResidualZllJet` | via UL18 hot map (data only in coffea) |

≠ cleaning cone (0.4 vs 0.3) and NanoAOD-index veto; ≠ PU ID; ≠ veto-map scope (probe vs any jet) and MC treatment.

---

## 11. Event selection

| Step | JS (`RunL3ResidualZllJet.cpp`, `RunL3ResidualZllJet.json`) | NA (`analysis.py`, `ZbHistograms.py`) |
|---|---|---|
| Order | HLT → golden → leptons+Rochester → Z → JEC → jets → Δφ → JVM(probe) → α → MET → response cut | golden → HLT → MET filters → leptons → Rochester → Z → lepton pT → drClean → JEC → leading jet → JVM → Δφ → jetId |
| Δφ(Z, jet1) | \|Δφ − π\| < 0.44 (`:203-205`) | \|Δφ − π\| ≤ 0.44 (`ZbSelection.py:104-110`) |
| jet2 for α | 2nd-highest-pT jet with pT ≥ 12 passing lepton cleaning (no jetId, no η cut) (`pickRecoJets`) | 2nd jet in the cleaned, corrected, pT-sorted `Jet` collection (no pT/η cut); a zero-pT dummy is appended so jet2 always exists (`ZbHistograms.py:258-274`) |
| α | pT(jet2)/pT(Z); **hard cut α < 1.0**; `minPtJet2InAlpha = 30` present but the floor is commented out (`:212-216`) | pT(jet2)/pT(Z) with pT(jet2) := 0 if < 15 (`:289-292`); no hard cut |
| α categories | `HistAlpha` cumulative α < 1.0, 0.5, 0.2, 0.1 (`alphaCuts`); `HistL3Residual` filled for α<1.0 only | `a030` (α<0.3), `a100` (α<1.0) |
| Response window | 0.3 < R_bal < 1.7 **and** 0.3 < R_MPF < 1.7 (`:236-241`) | none |
| \|η(jet1)\| | ≤ 1.3 hard | histogram categories: `eta_00_13`, `eta_00_25`, 19 narrow + 5 wide \|η\| bins (`ZbHistograms.py:39-70`) |
| Extra MC cuts | `passMatchedGenVtx` and pT-hat filter available but **disabled** (`:153`) | none |
| Other categories | flavour (`Jet_partonFlavour`) | b/c/quark/gluon tags (DeepFlav), gen-flavour (`ljetGenFlavor`), PSWeight |

≠ α (floor, hard cut, categories), response window, probe η treatment.

---

## 12. Response mathematics

Notation: **Z** = Z p⃗_T (Rochester-corrected leptons in both), **j1** = probe jet, **jn** = other jets, **MET** = type-1 MET (§12.2), pT² = pT(Z)².

### 12.1 Formulae

| Quantity | JS (`Hist/cpp/MathHdm.cpp:76-118`) | NA (`ZbHistograms.py:297-305`) | Same? |
|---|---|---|---|
| R_bal (DB) | pT(j1)/pT(Z) | pT(j1)/pT(Z) | = |
| R_MPF | 1 + MET·Z/pT² | 1 + MET·Z/pT² | = (given same MET) |
| R_MPF1 | 1 + MET1·Z/pT², MET1 = −(Z + j1) ⇒ −j1·Z/pT² | −j1·Z/pT² | = |
| R_MPFn | METn·Z/pT², METn = −Σjn | −(Σ_all jets − j1)·Z/pT² | = in form; **Σjn differs**: JS = jets with pT ≥ 12 and `muonIdx==−1` excluding probe (ΔR cleaning *not* re-applied, `PickZllJet.cpp:458-472`); NA = all cleaned jets incl. pT<12 |
| R_MPFu | METu·Z/pT², METu = MET + Z + j1 + Σjn | −METuncl·Z/pT², METuncl = −MET − Σjets − Z | = |
| R_MPFnu | METn + 1.1·METu | — | JS only |
| MPFx, MPF1x | Z rotated by +90° | same | = |
| Identity check | MPF = MPF1 + MPFn + MPFu enforced to 1e-4 (`:166-183`) | — | |
| Binning variable | pT(Z), `binsPt = [15,20,25,30,35,40,45,50,60,70,85,105,130,175,230,300,400,500,700,1000,1500]` (`VarBin.json:6-7`) | pT(Z), `bins_zpt = [12,15,20,…,1500]` (`ZbHistograms.py:29`) — identical above 15 | = |
| Storage | `TProfile` (`p1Resp*InTagPt`), `TProfile2D` vs (η_probe, pT_Z), TH1 of responses 0–2 (`HistL3Residual.cpp`) | `TH2` (pT_Z × response, y ∈ [−3.99, 6.01] step 0.02); `post_process.py:69-103` makes per-bin mean + `ProfileX` | ≈ (mean equivalent up to the JS 0.3–1.7 event window and NA y-range) |
| Gen response | `HistObjGenReco` pT(genZ) vs pT(Z), pT(genJet) vs pT(j1); gen jet = closest `GenJet` with pT>10 within ΔR<0.2 (`PickGenJet.json:6`, `PickGenJet.cpp:115-142`) | none | JS only |

### 12.2 MET entering MPF (largest math difference)

| | JS (`ScaleMet.cpp:43-79`, `ScaleJet.cpp:67-69,116,185-192`) | NA coffea (`JetCorrections.py:435-461`, `recalculateMET2`) | NA RDF C++ (`JetCorrections.cpp:913-1043`) |
|---|---|---|---|
| Start | **RawMET** (PF) | **ChsMET** (raw CHS) | RawMET (Run 2) |
| Jet input | pT_raw × (1 − `Jet_muonSubtrFactor`) | corrected jets as stored (no μ subtraction) | pT_raw × (1 − `muonSubtrFactor`) |
| Reference (L1) | L1FastJet on μ-subtracted raw | separate **L1RC** correction set (`*L1RC*` text files) | L1FastJet on μ-subtracted raw |
| Jet selection for propagation | raw(1−μ) ≥ 10 **and** pT_final > 15 **and** \|η\| < 5.2 **and** (neEmEF+chEmEF) < 0.9 | corrected pT > 15 only | pT_final > 15, \|η\| < 5.2, EMF < 0.9 |
| JER in MET (MC) | yes (ptFinalForMet includes JER) | yes (smeared pt and pt_l1rc) | yes |
| Lepton correction | intended `p4CorrMet += p4RawTag − p4Tag` is a **no-op** (§16) | none | none |
| Levels in "final" | as for jets: L1+L2 (+L2Res data) in derivation mode | L1+L2+L3+L2L3Res | L1+L2 (+L2L3Res data) |

≠ ChsMET vs RawMET is a genuine physics difference (different unclustered energy); the rest is second order but should be aligned (μ-subtraction, EMF cut, 10 GeV raw floor).

### 12.3 L2Residual mode
JS also runs Z+jet in `L2Residual` mode (`RunL2ResidualZllJet.cpp`, η-binned, `binsPtL2Residual = [15,60,120,300,480,1500]`, `binsEtaL2Residual` = 36 standard JEC η edges). NA covers this with the `etaNarrow`/`etaWide` categories at α<1.0. Not compared in detail here.

---

## 13. Event weights

| Component | JS MC (`ScaleEvent.cpp:102-138`, `WeightBreakdown.cpp`, `RunL3ResidualZllJet.cpp:247-267`) | NA MC (`analysis.py:150-157`, `post_process.py`) |
|---|---|---|
| Generator | genWeight / ⟨genWeight⟩ | sign(genWeight) |
| σ·L/N | 1000·L_year·σ/N_nano | σ·L_data/N_skim (post-process) |
| Pileup | correctionlib nominal | data/MC histogram ratio |
| L1 prefiring | `L1PreFiringWeight` **only for 2018** (`:116`) | none |
| Lepton SFs | Π over the two Z leptons of ID×Iso×Trig (μ) / ID×Reco×Trig (e) | none |
| Trigger SF | inside lepton SF (single-lepton SF, see §3) | none |
| Systematic weight | ISR/FSR/PDF/Q² via `Systematics` (Base = 1; `PSWeight` is never bound in `SkimAdapter.cpp:48`, so all variations evaluate to 1) | PSWeight axis in dedicated 3-D histograms |
| Where applied | base weight (gen × σL × PU × prefiring) for cutflow and `HistAlpha`; lepton SFs only after `passL3Residual`, so `HistL3Residual` and `HistAlpha` carry different weights | single `events.weight` everywhere |
| Data | 1 | 1 |

≠ prefiring (and wrong year in JS), lepton/trigger SFs.

---

## 14. Systematics infrastructure
- JS: `Systematic` token (IsrUp/Down, FsrUp/Down, PdfUp/Down, QsqrUp/Down) — but `PSWeight` is not bound in the skim adapter and PDF/Q² return 1, so L3 Zll output has no working variation; JEC uncertainty band class present but commented out in Zll; JER up/down available in correctionlib call (`syst` argument). `HemVeto` (run ≥ 319077, MC weight 0.65) and `passMatchedGenVtx` are active only in the L2 runner (`RunL2ResidualZllJet.cpp:82,117,152-156`), and there the lepton SF is applied to the first Z lepton only (`:164-166`).
- NA: PSWeight 3-D histograms (`hPSW_*`); RDF C++ path has full JES source splitting and JER η/pT-binned variations (`JercFileAndTagNamesAK4.json` `ForUncertaintyJES*/JER*`) — not wired into ZbAnalysis.

---

## 15. Outputs

| | JS | NA |
|---|---|---|
| Per-cutflow dirs | `Base/passSkim … passL3Residual` (`RunL3ResidualZllJet.json:2-13`) with `HistCutflow`, `HistWeightQA` | `configInfo/{unweighted,weighted}_counter`, `pu_orig/pu_corr/pu_data`, `lumi`, `isdata`, `JEC used` |
| Response | `passL3Residual/HistL3Residual/p1Resp{Db,Mpf,Mpf1,Mpfn,Mpfu,Mpfnu}InTagPt`, `p2Resp*InTagPtProbeEta`, `h1EventInResp*`, `p1{Tag,Probe,Met,Other,Unclustered}PtInTagPt` | `{data,mc}/<eta>/zpt_{db,mpf,mpf1,mpfn,mpfu,mpfx,mpf1x,corr,res}_zmmjet[_a030|_a100][_btag…]` TH2; plus `zpt_mass`, `zpt_{npv,rho,mu,chf,nhf,cef,nef}`, `RawNEvents`; `post_process.py` → `jme_ZplusJet_vX.root` with `*_graph`, `*_h2d`, `*_profile` |
| α scans | `passDeltaPhiTagProbe/HistAlpha/*` (per α cut, α profiles for 175<pT<230) | via `_a030/_a100` only |
| Kinematics | `HistObjP4` Tag/Probe, `HistPfComp`, `HistFlavor`, `HistTime` (data) | `zpt_*` PF fractions |

---

## 16. Code-health findings (to fix before or during sync)

### JERCSW
1. `RunL3ResidualZllJet.cpp:175-176,224` — `p4RawTag = p4Tags.at(0)` is taken after `ScaleMuon/ScaleElectron::applyCorrections` overwrote `Muon_pt`/`Electron_pt`; `p4CorrMet += p4RawTag − p4Tag` therefore adds zero. If the intent is to propagate Rochester/scale corrections to MET, the uncorrected Z must be built before `applyCorrections`.
2. `ScaleEvent.cpp:116-122` — L1 prefiring weight applied for `Year2018` only; ECAL prefiring maps exist for 2016 and 2017, and `L1PreFiringWeight_Nom` in 2018 is the muon-only weight. Likely inverted condition.
3. `Hist/config/ScaleMuon.json` — `muIdSfHist = NUM_TrkHighPtID_DEN_TrackerMuons_abseta_pt` while the selection uses `Muon_tightId`; should be `NUM_TightID_DEN_TrackerMuons_abseta_pt`. Trigger SF histograms are single-muon (`IsoMu24/27`) but the event trigger is `Mu17_Mu8`; applying it twice per event is not a valid dimuon efficiency correction.
4. `RunL3ResidualZllJet.json:18` `minPtJet2InAlpha: 30` is read but the corresponding condition is commented out (`RunL3ResidualZllJet.cpp:216`); `maxTagEta: 1.3` in the same file is unused (the η(Z) cut comes from `PickZllJet.json:26`).
5. `PickZllJet.cpp:458-472` — the Σ(other jets) used for MPFn skips the ΔR(jet, lepton) cleaning that is applied when choosing jet1/jet2, so a jet within ΔR<0.4 of a lepton (but with `muonIdx==−1`) enters MPFn/MPFu inconsistently.
6. `PickZllJet.json:26` `tagPick.maxEta = 1.3` — an η(Z) requirement; not present in NA nor in the standard L3Res Z+jet selection. Confirm.

### NanoAnalysis
1. `ZbAnalysis/analysis.py` (coffea) is out of step with `Framework/`: `METCleaning()` dispatches to the RDF implementation (`METCleaning.py:3-8`) and will fail on awkward arrays; `PileupWeight.PileupWeight(pu_data, pu_mc)` no longer matches the `RDFPileupWeight(multicrab, datasets)` signature (`PileupWeight.py:8-11,36`); `LumiMask.LumiMask(dataset)` returns the RDF class (`LumiMask.py:21-24`); `JetCorrections.py:1-5` has the coffea imports (`extractor`, `JECStack`, …) commented out. `analysis_RDataFrame.py` is a stub (`HLT_IsoMu24` filter + `PV_npvs` histogram).
2. `JetCorrections.py:491` `jecSmearFactor = normal(1, σ)·√(SF²−1)` — differs from the documented KIT formula `1 + N(0,σ)·√(SF²−1)` (comment on `:487`); if the coffea path is revived, this scales MC jets by ≈ √(SF²−1) ≈ 0.5. The resolution is also evaluated at `JetPt = pt_raw` (`:474-478`) rather than the corrected pT, and there is no gen-matched (scaling) branch.
2b. `RochesterCorrections.py:17-20` — `'APV' in run` can never be true with the `run` string produced by `multicrabdatasets.getRun` (`:259-270`), so 2016 preVFP uses the postVFP Rochester file.
2c. `tools/plotting.py:453-471` — MC normalised by the raw skim event count while events are weighted by sign(genWeight); for aMC@NLO this under-normalises the yield by ⟨sign(genWeight)⟩. Cross-section lookup for the task names `DYJetsToLL_M_50_LO/_NLO/_herwig7` returns `None` (`tools/crosssection.py:37-41,504-529`).
2d. `multicrabdatasets.getRun` (`:259-270`) returns a single era string for the whole multicrab; `JetCorrections.JEC` uses it as the data era key (`:282-283`), so mixed-era multicrabs get one era's JEC.
3. `ZbSelection.py:44-51` — electron selection not implemented (no ID/iso/gap veto).
4. `NanoAODSkim/test/keep_and_drop_ZbAnalysis.txt:12` — only `…_DZ_Mass8` is kept; the 2016 dimuon path `HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ` is dropped (`keepmatch` is a prefix regex; `_DZ_Mass8` does not match `_DZ`).
5. `NanoAOD_ZbAnalysisSkim.py:99-168` — skim trigger OR includes single-lepton and prescaled paths; harmless once the analysis trigger is applied, but inflates skims.
6. `post_process.py:158` merges every non-data dataset into "MC"; with the default `analysis.py` whitelist this sums LO-MLM + NLO DY + TTJets.
7. `JetCorrections.py:53-70` — 2016Post mixes Summer19UL16_RunFGH_V7 (F) with Summer20UL16_RunGH_V1 (G, H) and Summer20UL16_V1 MC; `2017` uses V6 while the RDF JSON uses V5.

---

## 17. Proposed synchronisation baseline (for discussion)

A minimal common selection both codes can implement:

1. Data: DoubleMuon / DoubleEG(2016-17) / EGamma(2018) JMENanoAODv9 as listed; MC: `DYJetsToLL_M-50 amcatnloFXFX` only, σ = 6077.22 pb (or agree on 5765.4), w_gen = genWeight/⟨genWeight⟩.
2. HLT: Zmm `Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ` (2016) / `_DZ_Mass8` (2017-18); Zee `Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ` (2016) / `…_IsoVL` (2017-18) — decide DZ vs non-DZ for 2017-18 once.
3. MET filters: JetMET UL list (add `BadPFMuonDzFilter` in JS; add `EcalDeadCell…` + `BadPFMuonDz…` to NA 2016).
4. Muons: tightId, pfRelIso04 < 0.15, |η| < 2.3, |dxy| < 0.2, |dz| < 0.5, pT > 20/10 (or 20/20 — decide), exactly one OS pair, 2 ≤ N ≤ 3; Rochester with `GenDressedLepton` ΔR<0.2 matching and deterministic seed.
5. Electrons: cutBased tight, |η_SC| < 2.4 with 1.4442–1.566 veto, pT > 25/15 (or 25/25).
6. Z: |m − 91.1876| < 20, pT > 15, **no η(Z) cut** unless justified.
7. Jets: AK4 CHS, Summer19UL V7/V7/V5/V5 JEC (L1FastJet+L2Relative; data +L2Residual for derivation), JER Summer20UL16_JRV3 / Summer19UL17_JRV3 / Summer19UL18_JRV2 hybrid, all jets corrected; clean ΔR(jet, ℓ) < 0.4 (and `muonIdx/electronIdx == −1`); probe: TightLepVeto, |η| < 1.3, pT > 12; PU ID: decide (off is simpler).
8. Δφ: |Δφ − π| < 0.44. α = pT(jet2)/pT(Z) with jet2 the 2nd cleaned jet with pT > 15 (α = 0 otherwise); α-cut set {0.3, 1.0} ∪ {0.1, 0.2, 0.5}; no response window (or the same one in both).
9. MET: Type-1 from RawMET with μ-subtracted jets, L1FastJet reference, propagate jets with pT_corr > 15, |η| < 5.2, EMF < 0.9; propagate Rochester Δp⃗_T of the two leptons.
10. Weights: PU (agree on JSON vs histogram), no prefiring in 2018, TightID SF if SFs are kept; PSWeight variations optional.
11. Histograms: TProfile of DB/MPF/MPF1/MPFn/MPFu vs pT(Z) in `[15,…,1500]`, plus TH2 with a common y range for cross-checks.

