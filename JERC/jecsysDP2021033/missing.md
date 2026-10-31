# Missing pieces for reproducing DP-2021-033 with jecsys

Checkout: jecsys commit d59d5f5 (tag DP-2021-033-Run2combo), run on lxplus el9, 2026-10-29.
Update 2026-10-30 (a): jecsys moved outside CMSSW; build re-checked with the stock el9 ROOT (sec. 1a).
Update 2026-10-30 (b): second delivery from Mikko in `DP2021033V2/` (sec. 2f). Everything in sec. 2c is now covered
EXCEPT `rootfiles/hadWMC16GHV7_JEC.root`, which is needed by every epoch; a labelled stand-in is in place (sec. 2f).
Strategy agreed with Ravindra: finish ONE year first (starting with 2016GH), then the next.
Chain followed (README.md "EXPERTS" section plus Mikko's note in DP2021033/copyFilesForRavindra.sh):

    for IOV in 2016BCDEF 2016GH 2017BCDEF 2017H 2018ABCD:  root -b -q 'mk_reprocess_RunEpoch.C("IOV")'
    root -b -q recombine.C
    root -b -q 'mk_reprocess_RunEpoch.C("Run2Test")'

Each `mk_reprocess` call runs reprocess -> softrad3 -> globalFitSyst -> globalFitRenormPF -> globalFitL3Res.
**Order matters**: globalFitL3Res.C reads `sys/hjesfit` from the reference IOV's `rootfiles/jecdata<refIOV>.root`
(L981, `isRefIOV ? "herr_ref" : "sys/hjesfit"`), and that histogram is written only by the globalFitL3Res run of the
reference IOV itself (L2776-2795). Reference IOVs are 2018ABCD, 2017BCDEF, 2016BCDEF, Run2Test (L389); 2016GH's
reference is 2016BCDEF (L382-387). So per year: run the reference epoch first (2016BCDEF before 2016GH; 2017BCDEF before 2017B-F;
2018ABCD before 2018A-D), otherwise 2016GH aborts with `Assertion hjesfitref failed` (seen 2026-10-30).
`mk_drawJetCorrectionUncertainty.C` / `mk_testSources.C` (README steps 2 and 3) were not reached.

---

## 0. How far the chain gets now (updated 2026-10-30, 10:00)

**The whole documented chain now runs end to end** with the HEAD code (d59d5f5) and stock ROOT 6.40.04, outside CMSSW:

| Step | Result (globalFitL3Res "Global chi2/ndf", data points) | DP-2021/033 figure (p.12) |
|---|---|---|
| 2016BCDEF | OK, 437.6 / 212, 221 points | 96.4 / 151 |
| 2016GH | OK, 245.2 / 214, 223 points (no inclusive jets) | 164.5 / 252 (legend includes "Incl. jet wrt 2016 early") |
| 2017BCDEF | OK, 702.4 / 214, 223 points | 185.9 / 63 |
| 2018ABCD | OK, 508.5 / 214, 223 points | 143.9 / 138 |
| recombine | OK, writes `rootfiles/jecdataRun2TestData.root` | - |
| Run2Test | OK, 717.3 / 216, 225 points | p.13 shows no chi2 |

Outputs: `rootfiles/jecdata<epoch>.root`, `rootfiles/globalFitL3Res_emat_<epoch>.root`, `pdf/<epoch>/globalFitL3res_{raw,orig,shifted,doublyshifted,hsrc,pfjet,*_kfsr}.pdf`
(+ `.root` canvases), fit parameters appended to `textFiles/globalFitL3Res.txt`. Reruns are reproducible bit for bit (fit parameters identical over 3 runs).
Each `globalFitL3Res` ends with `double free or corruption (fasttop)` (exit code 6) *after* the last `SaveAs` and after the jecdata file is closed; outputs are complete, ignore it.
Running Run2Test overwrites the tracked `rootfiles/jecdataRun2Test.root` and 2018ABCD overwrites tracked `rootfiles/jecdata2018ABCD.root` (`git checkout --` restores Mikko's copies).

**But the HEAD configuration does not reproduce the per-year DP-note fits.** Diagnosis so far (2016, comparing our `jecdata2016{BCDEF,GH}.root` with Mikko's
`DP2021033/jecdata2016{BCDEF,GH}.root` of 2021-10-05, i.e. the files behind the DP-note 2016 plots):
- The raw data/MC input graphs (`ratio/eta00-13/{mpfchs1,ptchs}_*_a*`, TGraphErrors) agree to <2e-3 -> reprocess inputs are the same.
- What differs: FSR corrections from softrad3 (`fsr/hkfsr3_*`, e.g. gamma+jet MPF FSR -0.2% now vs -1.3% then), the HDM combos `hdm_*` (also their pT ranges:
  archived Z+jet MPF covers 37-202 GeV only, gamma+jet 265-1100, multijet >847; ours cover 17-600, 152-2375, 133-2003), `herr_l2l3res`/`hrun1` (old-JEC reference),
  `sys/jer_multijet`, `sys/zee_gamjet_eig*`, and therefore `sys/hjesfit` (1% at 10 GeV, 0.5% at 100 GeV for BCDEF).
- Number of fitted points differs (221 vs 160 for BCDEF; 223 vs 261 for GH), so the selection/ranges in globalFitL3Res differ, not only the FSR.
- Reason: the fit macros changed by ~2000 lines between the DP-note commits (e5a0f0b 2021-10-05 .. c38ed3d 2021-10-14) and HEAD; Mikko's Nov-2022
  "Revert ... to DP_2021" commits targeted the *Run 2 combination* ("Run2combo" tag), not the per-year plots.
- Mikko's archived `rootfiles/jecdataRun2Test.root` (tracked, dated 2022-04-04) is a later iteration, not the DP-note version, so it is not a reference either.
- `mk_reprocess.C` at c38ed3d has reprocess/softrad/softrad3/globalFitSyst commented out: the DP-note plots were made by running globalFitL3Res alone on pre-made jecdata files,
  which is exactly what `DP2021033/jecdata2016{BCDEF,GH}.root` and the tracked `jecdata2018ABCD.root` (byte-identical to the DP2021033 copy) are.

Experiment in progress: git worktree `../jecsys_oct2021` at c38ed3d (DP-note-era code), inputs wired by untracked symlinks only
(`rootfiles/*` -> `DP2021033/*`, `../gamjet/files/*` -> `DP2021033{,V2}/*`, JEC text files, `../JERCProtoLab/Summer19UL16/L3Residual_incljet/drawDeltaJEC_16ULJECV5_vsBCDEF.root` -> V2 copy),
Mikko's archived `jecdata2016{BCDEF,GH}.root` copied into its `rootfiles/`. Result: see sec. 0a.
Not available for that code: `../JERCProtoLab/Summer19UL16/L3Residual_incljet/drawDeltaJEC_16ULJECV7_vsBCDEF.root` (reprocess.C L443 at c38ed3d; only matters if reprocess is rerun there).

Original table (2026-10-29/30 morning, before DP2021033V2) kept for history:

| Step | Result then | Blocker then |
|---|---|---|
| 2016BCDEF / 2016GH | reprocess + softrad3 OK, globalFitSyst aborted | `GamHistosFill_data_2018ABCD_v19.root` (now in V2) |
| 2017BCDEF / 2018ABCD | reprocess aborted at the gamma+jet input | `GamHistosRatio_{2017BCDEF,2018ABCD}_P8_v18.root` (now in V2) |
| 2017H | reprocess aborts at reprocess.C:2779 | `jme_bplusZ_merged_v38_muon2017H.root` without `statistics_mpfchs_zmmjet_a100` (V2 copy has it; 2017H not rerun yet) |
| recombine / Run2Test | segfault / `hmzee` abort | needed the four reference jecdata files (now produced) |

### 0a. DP-note-era code (c38ed3d) on Mikko's archived 2016 inputs (2026-10-30, 10:10)

Result: **no committed 2021 code version matches the archived 2016 files either.**
- c38ed3d (2021-10-14) `globalFitL3Res("2016BCDEF","MJDJ_gam_z_hadw")` on `DP2021033/jecdata2016BCDEF.root` -> `Assertion hfsr failed`, `fsr/hkfsr3_ptchs_gamjet not found`.
  The archived 2016BCDEF file has only `fsr/hkfsr_*_gamjet` and `fsr/hkfsr2_*_gamjet` (alpha-extrapolation FSR from softrad.C), no `hkfsr3_*_gamjet` (HDM FSR from softrad3.C),
  while both e5a0f0b (2021-10-05, the day the archive was written) and c38ed3d read `fsr/hkfsr3_<method>_gamjet` for a reference IOV (globalFitL3Res.C L1027 / L1067).
  2016GH then fails for lack of the 2016BCDEF `herr_ref` (9 points, segfault). The 2016GH archive does contain `hkfsr3_*_gamjet`, so the two archived files were not even made with the same configuration.
- HEAD (d59d5f5) `globalFitL3Res` on the archived 2016BCDEF file: same `Assertion hfsr` on `fsr/hkfsr3_ptchs_gamjet` (HEAD code and the archived inputs are incompatible too).
- No commit touched the fit macros between 2021-09-10 and 2021-10-14 except c38ed3d, so the 2016 DP-note plots came from an uncommitted working state (or a flag setting such as `dofsrcombo2`) on Mikko's machine.

=> Reproducing the per-year DP-note chi2 needs information from Mikko (see the asks list in sec. 2f), not more local archaeology.
What *can* be compared now with the public note (https://cds.cern.ch/record/2792322/files/DP2021_033.pdf, p.12): our `pdf/<epoch>/globalFitL3res_doublyshifted.pdf`
has the same style and the same gross shape (2016 early: response ~0.975 at 50 GeV rising to ~1.00 at 2 TeV), but extra Z+jet points at 17-35 GeV, inclusive jets drawn, and a different chi2.

Worktree housekeeping: `../jecsys_oct2021` (c38ed3d + the `tools.h` compile fix, untracked symlinks, Mikko's archived 2016 jecdata copies in its `rootfiles/`) can be removed with
`git worktree remove --force ../jecsys_oct2021`. Also created for it, harmless for HEAD: `../gamjet/files/*` (symlinks to DP2021033{,V2}) and
`../JERCProtoLab/Summer19UL16/L3Residual_incljet/drawDeltaJEC_16ULJECV5_vsBCDEF.root` (symlink to the V2 copy).

---

## 1. Environment problems (fixed locally, nothing to request)

| Problem | Symptom | Fix applied |
|---|---|---|
| CMSSW `cmsenv` shadows the local `CondFormats/JetMETObjects` copy | ACLiC: `redefinition of getFloat/getUnsigned/... in Utilities.cc` | Not enough to add `-I`; see next row |
| CMSSW autoloads its own `libCondFormatsJetMETObjects.so` next to the ACLiC-built one | `malloc(): unsorted double linked list corrupted` / segfault while parsing the first JEC text file | **Done (2026-10-30): jecsys now lives outside CMSSW.** Do not source `cmsenv` in the shell that runs the chain. Any ROOT without CMSSW works, see sec. 1a; the LCG `env -i` recipe is no longer needed. |
| `jec-fit-prototype` not checked out | `FindDynamicLibrary: .../jec-fit-prototype/lib/libjecfit does not exist` | Harmless, library is not used by this chain |
| `tools.h` vs `tools.C` mismatch (`diffGraphs` has 4 args in .C, 2 in .h) | ACLiC error in tools.C and globalFitRenormPF.C | Added `double c1=1, double c2=1` defaults to the declaration in tools.h (matches upstream jecsys) |
| `tdrstyle_mod15.C` uses undeclared `lumi_136TeV` | ACLiC error in reprocess/softrad3/globalFitL3Res | Added a `TString lumi_136TeV` placeholder next to the other lumi strings |
| Crashed `reprocess` runs truncate their `RECREATE`d output | tracked `rootfiles/jecdata2018ABCD.root` and `rootfiles/jecdataRun2Test.root` became 256-byte stubs | restored with `git checkout --`; re-check after every failed 2018ABCD / Run2Test run |

### 1a. ROOT version check (2026-10-30, outside CMSSW)

Question was whether an older ROOT is needed to read the TGraphs in the inputs. Answer: **no**. Tested with the same
force-rebuild (`.L X.C++g`) of all 13 ACLiC units (6 CondFormats sources, tools, Flavor, reprocess, softrad3, globalFitSyst,
globalFitRenormPF, globalFitL3Res):

| ROOT | Source | Compile | Run 2016GH chain |
|---|---|---|---|
| 6.40.04 (`/usr/bin/root`, rpm `root-6.40.04-4.el9`, default in the login shell) | stock el9 | 13/13 OK, 0 errors, ~3.5 min | reprocess + softrad3 OK, stops at the same `GamHistosFill_data_2018ABCD_v19.root` assert (sec. 2c) |
| 6.32.02 (LCG_106) | cvmfs | 13/13 OK (2026-10-29 run) | same |
| 6.28.04 (LCG_104) | cvmfs | 13/13 OK, 0 errors (scratch copy of the sources) | not run |

- `rootfiles/jecdata2016GH.root` produced with 6.40.04 and with 6.32.02 was compared object by object: 11866 histograms/graphs/functions, 0 differences above 1e-6 relative, nothing missing. The ROOT version does not change the result.
- All 234 input `.root` files reachable from reprocess/softrad3/globalFit* (jecsys `rootfiles/`, `DP2021033/`, `../JERCProtoLab/...`) were opened with 6.40.04 and every key read back. They were written by ROOT 5.32 up to 6.24. About 3.5 million TGraph-family objects were read with **zero** streamer/version errors. So the "old TGraph" worry is not a ROOT 6.40 problem.
- The only read failures are file corruption, identical in 6.28/6.36/6.40, i.e. not version related: see sec. 2e (`rootfiles/jecdataBCDEF_V4.root`, `DP2021033/jecdata2017BCDEF.root`).
- Practical note: ACLiC products (`*_C.so`, `*_C.d`, `*_ACLiC_dict_rdict.pcm`, `*_cc.so` under `CondFormats/JetMETObjects/src/`) are tied to the ROOT that built them. When switching ROOT version delete them or force a rebuild, otherwise ROOT tries to load a stale library. They are currently built with 6.40.04.
- Stale ROOT errors that are normal in the 2016GH run and not a problem: `FindDynamicLibrary ... libjecfit does not exist` (sec. 1), `TF1::GetX ... not a valid interval` / `BrentRootFinder` in softrad3, `TDirectoryFile::mkdir: fsr exists already`.
- The login shell still exports `SCRAM_ARCH` and defines `cmsenv`; that is harmless as long as `cmsenv` is not run (`CMSSW_BASE` is empty). `LD_LIBRARY_PATH` carries `../JERCSW/Hist/corrlib/lib` (correctionlib) and did not interfere.

## 2. ROOT input files

### 2a. Provided by Mikko in `DP2021033/` (reprocess.C already repointed there)
Multijet UL17/UL18, `drawDeltaJEC_Run2_vsUL5X.root`, PF composition UL16/UL18 and low-PU,
hadronic W (all years), 2016 `GamHistosRatio` v18, all `jme_bplusZ_merged_*`, `P8_dijet_45M_TH2D_correct_weighting.root`.

### 2b. Available in the sibling checkout `../JERCProtoLab` (paths unchanged, they work)
UL16 multijet V7 closure, UL16 hadronic W, Z+jet for all years, UL18 gamma L1L2Res.

### 2c. Was missing on 2026-10-29, needed by the active configuration (CorLevel = L1L2L3Res). Status after DP2021033V2 in the last column

| File | Used by | Epochs blocked | 2026-10-30 status |
|---|---|---|---|
| `../gamjet/files/GamHistosRatio_2018ABCD_P8_v18.root` | reprocess.C L697 (gamma+jet) | 2018ABCD (and 2018A-D), hence recombine and Run2Test | in V2; reprocess.C repointed to `DP2021033V2/` |
| `../gamjet/files/GamHistosRatio_2017BCDEF_P8_v18.root` | reprocess.C L704 (gamma+jet) | 2017BCDEF (and 2017B-F), hence recombine and Run2Test | in V2; reprocess.C repointed to `DP2021033V2/` |
| `../gamjet/files/GamHistosFill_data_2018ABCD_v19.root` | globalFitSyst.C L181 (`doGamGains`, asserted) | all epochs | in V2 (has `control/pgain1vspt`, `pgain6vspt`); globalFitSyst.C repointed |
| `rootfiles/hadWMC16GHV7_JEC.root` | globalFitSyst.C L277 (`doHadWfsr`, asserted); produces `hdm_hadw` needed by globalFitRenormPF | all epochs | **STILL MISSING.** Mikko's `copyFilesForRavindraV2.sh` line for `../jecsys2020/rootfiles/hadWMC16GHV7_JEC.root` has no destination, so it was not copied. Stand-in in place, see sec. 2f. **Ask Mikko again.** |
| `../JERCProtoLab/Summer19UL16/L3Residual_incljet/drawDeltaJEC_16ULJECV5_vsBCDEF.root` | globalFitL3Res.C L431 (asserted) | 2016BCDEF, 2016GH | in V2 (`jet_Run16UL{BCD,EF,BCDEF,GH}_fwd`, matches the code); globalFitL3Res.C repointed |
| `rootfiles/drawDeltaJEC_18UL_JECv3.root` | globalFitL3Res.C L433 (asserted) | 2018ABCD | in V2, byte-identical to the tracked `rootfiles/drawDeltaJEC_18UL_JECV3.root` (only the case of `v3` differed); copied under the lowercase name |
| `rootfiles/drawDeltaJEC_Run2_vsUL4X.root` | globalFitL3Res.C L435/437 (asserted) | Run2Test, 2017H | in V2 from `../jecsys2020` (Mikko: "not primary input, might be incorrect"); has `jet_RunUL{16,17,17H,18,4X}_fwd`, matches the code; copied to `rootfiles/` |

Note on `drawDeltaJEC_*`: `DP2021033/drawDeltaJEC_Run2_vsUL5X.root` exists but contains histograms
`jet_RunUL16APV_fwd`, `jet_RunUL16GH_fwd`, `jet_RunUL17_fwd`, `jet_RunUL18_fwd`, `jet_RunUL17H_fwd`, `jet_RunUL5X_fwd`,
whereas globalFitL3Res.C L1002-1010 looks for `jet_Run16UL<era>_fwd`, `jet_Run18UL<era>_det`, `jet_Run17UL_fwd3`, `jet_RunUL4X_fwd`.
So either the original files are needed, or globalFitL3Res.C must be adapted to the vsUL5X file (as reprocess.C already was).

### 2d. Missing but only needed if CorLevel is switched to L1L2Res (not needed now)
- `../JERCProtoLab/Summer19UL16/L3Residual_multijet/multijet_UL2016{BCD,EF,BCDEF,FGH}_jecV5_jerV2.root`
- `../JERCProtoLab/Summer19UL17/L3Residual_Z/.../ZJetCombination_{Zmm,Zee}_..._Summer19UL17_JECV5_L1L2Res.root`
- `../JERCProtoLab/Summer19UL16/L3Residual_Z/APV/JEC_Combination_Zee/electrons_in_barrel/..._V3_L1L2Res.root`

### 2e. Files that exist but have the wrong content
| File | Problem |
|---|---|
| `DP2021033/jecdataRun2TestData.root` | 645 bytes, only an empty `mc` directory (identical in `missing/DP2021033.tar.gz`). Unusable. reprocess.C was reverted to read `rootfiles/jecdataRun2TestData.root`, the output of recombine.C. Needs the real file from Mikko, OR the two 2017/2018 gamma files so recombine can build it. |
| `DP2021033/jme_bplusZ_merged_v38_muon2017H.root` | reprocess.C L2779 expects `mc/eta_00_13/statistics_mpfchs_zmmjet_a100`; the file only has `statistics_rbal_*` / `statistics_resp_*` graphs. Version mismatch between file and code for the 2017H low-PU epoch. |
| `DP2021033/jecdata2017BCDEF.root` | 258 bytes (dated 2021-10-06), ROOT cannot even read the header (zombie). Not referenced by any macro, but it is presumably Mikko's archived 2017BCDEF output, i.e. a reference file that would be useful for comparison. Ask for the real one together with the Run2TestData file. |
| `rootfiles/jecdataBCDEF_V4.root` (tracked, commit 6a8c875) | 28 objects under `ratio/eta00-13/fsr/hkfsr2_*` and `ratio/eta00-13/sys/fjesfit` have corrupt zlib blocks (`R__unzip_header: error in header`); the committed git blob itself is corrupt, same failure in ROOT 6.28/6.36/6.40. Harmless for now: it is only opened for `CorLevel=="L1L2Res"` (reprocess.C L873-887) and the object it needs, `ratio/eta00-13/herr_ref`, reads fine. |

### 2f. Second delivery `DP2021033V2/` (2026-10-30) and how it was wired in

Contents (from `DP2021033V2/copyFilesForRavindraV2.sh`): the three gamma files, the three `drawDeltaJEC_*` files,
`jme_bplusZ_merged_v38_muon2017H.root`, `Summer19UL18_RunC_V3M1_DATA_L2L3Residual_AK4PFchs.txt`,
`mergeL2L3ResTextFiles_Run2Test_AK4PFchs.txt`, plus `cp_dpnote.sh` (which pdf/root outputs went into the DP note:
`pdf/2016GH/globalFitL3Res_doublyshifted_UL16V7GH.*`, `pdf/2016BCDEF/..._UL16V7BCDEF.*`, `pdf/BCDEF/globalFitL3Res_shifted.*` -> UL17V5, `pdf/2018ABCD/globalFitL3Res_shifted.*` -> UL18V5).
The `._*` files are macOS resource forks, ignore.

| Item | Action taken |
|---|---|
| gamma 2017/2018 ratio, gamma 2018 fill, drawDeltaJEC 16UL | code repointed to `DP2021033V2/...`, lines tagged `// DP2021033V2 path` (reprocess.C L697/L704, globalFitSyst.C L181, globalFitL3Res.C L431) |
| `jme_bplusZ_merged_v38_muon2017H.root` | reprocess.C L923 repointed to the V2 copy (has `mc/eta_00_13/statistics_mpfchs_zmmjet_a100`, the DP2021033 copy did not). 2017H only. |
| `drawDeltaJEC_18UL_JECv3.root`, `drawDeltaJEC_Run2_vsUL4X.root` | copied into `rootfiles/` (hardcoded names) |
| `Summer19UL18_RunC_V3M1_DATA_L2L3Residual_AK4PFchs.txt` | copied into `CondFormats/JetMETObjects/data/` (needed by 2018ABCD, reprocess.C L3476). Resolves the sec. 3 item. |
| `mergeL2L3ResTextFiles_Run2Test_AK4PFchs.txt` | Mikko's copy (from `../jecsys2020`, "not official, might be incorrect") replaces the locally regenerated one in `textFiles/`; the two differ in every parameter row. The regenerated one is still available as `textFiles/mergeL2L3ResTextFiles_Run2.txt` (output of the minitool). Resolves the sec. 3 item. Run2Test only. |
| `hadWMC16GHV7_JEC.root` | **not delivered**. `rootfiles/hadWMC16GHV7_JEC.root` is now a SYMLINK to `rootfiles/hadWMC16GHV7_JEC_STANDIN_from_jecdataRun2Test.root`, built by `minitools/mk_hadW_standin.C` (see `rootfiles/README_hadW_standin.txt`). globalFitSyst.C only uses the file as `hadw_fsr = 1 + (pup-pdw)/pmc` and `hadw_ptave_fsr = hadw_ptboth_fsr = (pup-pdw)/pmc`, and the file is the same for every epoch (UL16GH MC PSWeights), so the stand-in sets `pmm13bptave = pmm13bptave_FSRdw = 1`, `pmm13bptave_FSRup = 1 + hadw_ptave_fsr` from Mikko's archived `rootfiles/jecdataRun2Test.root`. Verified: reproduces the archived `hadw_fsr` bin by bin. What is NOT reproduced: the bin errors of `hadw_*_fsr` (the code does not propagate them into `hdm_hadw`, so the global fit inputs are unaffected). Replace the symlink by the real file when it arrives and rerun globalFitSyst onwards. |

Remaining asks for Mikko after V2:
1. `../jecsys2020/rootfiles/hadWMC16GHV7_JEC.root` (stand-in in use).
2. For comparison the real `jecdata2017BCDEF.root` / `jecdataRun2TestData.root` (both copies in DP2021033 are empty stubs, sec. 2e).
3. Which code state / switches produced the per-year DP-note fits (p.12): `DP2021033/jecdata2016BCDEF.root` has no `fsr/hkfsr3_*_gamjet`, so neither c38ed3d nor HEAD can even run on it (sec. 0a);
   2016GH's DP plot includes inclusive jets while `mk_reprocess.C` (then and now) fits 2016GH with `MJDJ_gam_z_hadw`; the HEAD fits use many more low-pT Z+jet points (221 vs 160 for 2016BCDEF).
   Ideally: his `globalFitL3Res.C`/`mk_reprocess.C` as of 2021-10-05/06, or the `pdf/2016*/globalFitL3Res_doublyshifted_UL16V7*.root` canvases listed in `cp_dpnote.sh`.

## 3. JEC text files (`CondFormats/JetMETObjects/data/`)

The repository ships none of the Summer19UL16 V7, Summer19UL17 V5, Summer19UL18 V5 text files that reprocess.C loads.
33 files were copied from `../JECDatabase/textFiles/<set>/` into `CondFormats/JetMETObjects/data/` (listed by `git status`),
and the LCG-ROOT test confirmed they parse and evaluate correctly.

Were still missing on 2026-10-29:

| File | Used by | Epochs blocked | 2026-10-30 |
|---|---|---|---|
| `CondFormats/JetMETObjects/data/Summer19UL18_RunC_V3M1_DATA_L2L3Residual_AK4PFchs.txt` | reprocess.C L3476 (`jecold`, old JEC undone in the global fit) | 2018ABCD | **delivered in V2 (from `../jecsys2020`), copied in** |
| `textFiles/mergeL2L3ResTextFiles_Run2Test_AK4PFchs.txt` | reprocess.C L3372/L3500 | Run2Test | **delivered in V2 (from `../jecsys2020`), replaces the regenerated file** |

The second one was regenerated with `root -b -q minitools/mk_mergeL2L3ResTextFiles.C` (needs `../JECDatabase`),
which writes `textFiles/mergeL2L3ResTextFiles_Run2.txt`; it was copied to the `_Run2Test_AK4PFchs.txt` name reprocess.C expects.
Whether this regenerated file is bit-identical to the one used for DP-2021-033 is not verified.
`V3M1` is a development version that exists only for UL16 in `../JERCProtoLab/Summer19UL16/global_fit/V3M1`; there is no UL18 V3M1 anywhere on disk.

## 4. Reference outputs available for comparison
- `rootfiles/jecdataRun2Test.root` (tracked): Mikko's archived Run2Test output, contains `hdm_hadw`, `ghdm_hadw`, `hadw_fsr`, etc.
- `../JERCProtoLab/Summer19UL16/global_fit/jecdata2016{BCD,EF,BCDEF,GH}.root`: archived UL16 outputs (older, V3M1/V5M1 era).

## 5. Local modifications made during this exercise
- 2026-10-30 run outputs (untracked unless noted): `rootfiles/jecdata{2016BCDEF,2016GH,2017BCDEF}.root`, `rootfiles/jecdata{2018ABCD,Run2Test}.root` (**tracked, now overwritten** by our runs; `git checkout -- rootfiles/jecdata2018ABCD.root rootfiles/jecdataRun2Test.root` restores Mikko's),
  `rootfiles/jecdataRun2TestData.root` (recombine), `rootfiles/globalFitL3Res_emat_*.root`, `pdf/{2016BCDEF,2016GH,2017BCDEF,2018ABCD,Run2Test}/*`, lines appended to `textFiles/globalFitL3Res.txt`.
- Logs of the verified runs are in the Claude scratch area under `/tmp/rverma/claude-93032/.../scratchpad/run_<epoch>.log` (not persistent); rerun with `root -b -q 'mk_reprocess_RunEpoch.C("<epoch>")' > log 2>&1` to regenerate.
- `doc/jecsys.tex` (+ `doc/jecsys.pdf`, 31 slides, 2026-10-30): end-to-end walkthrough of the 2016 chain, technical flow and physics per stage; figures from `root -b -q doc/mk_docplots.C` (writes `doc/figs/`) and from `pdf/2016*/`. Rebuild with `cd doc && pdflatex jecsys.tex` (twice).
- `mk_reprocess_epoch.C`: named-function twin of mk_reprocess.C (only needed for ROOT 6.28/cling; with 6.40 `mk_reprocess_RunEpoch.C` works).
- `reprocess.C`: input paths -> `DP2021033/` where the files only exist there (gamma 2016, W, b+Z, PF, multijet, incl. jet, low-PU eta map).
- `tools.h`, `tdrstyle_mod15.C`: compile fixes (sec. 1). Package moved out of CMSSW, built with stock ROOT 6.40.04 (sec. 1a).
- `CondFormats/JetMETObjects/data/`: +33 JEC text files from JECDatabase.
- `textFiles/mergeL2L3ResTextFiles_Run2*.txt`, `textFiles/mergeL2ResTextFiles_Run2.txt`: regenerated.
- `rootfiles/jecdata2016BCDEF.root`, `rootfiles/jecdata2016GH.root`: produced by reprocess+softrad3 (no global fit yet).
- `pdf/<epoch>/` directories created (empty or partial plots).
- Untracked `*_C.so`, `*_C.d`, `*_ACLiC_dict_rdict.pcm` build products can be deleted; they must be deleted when changing ROOT version (sec. 1a).
