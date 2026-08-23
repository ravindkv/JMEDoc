# RecoJets Package Overview

This README is a physics-first map of `RecoJets`, followed by a technical lookup
of the subpackages and files in this checkout. It documents maintained source,
configuration, data, documentation, test, and validation files. Generated
`__pycache__` files are intentionally ignored.

## Where to Start

For learning the package from the physics point of view, start in this order:

1. `Configuration`
   - This is the best entry point. It shows the reconstruction workflows:
     calorimeter towers, generator-level jet inputs, calo jets, PF jets, track
     jets, PF-cluster jets, JPT jets, jet IDs, and jet-track associations.
   - Start with `Configuration/python/RecoJetsGlobal_cff.py`, then read
     `RecoJets_cff.py`, `RecoPFJets_cff.py`, `RecoGenJets_cff.py`, and
     `GenJetParticles_cff.py`.

2. `JetProducers`
   - This is the core physics production package. It turns input constituents
     into reconstructed jet collections and adds jet-level observables such as
     rho, pileup ID, QG likelihood, N-subjettiness, ECFs, grooming, and top tags.
   - Start with `JetProducers/python/ak4PFJets_cfi.py`,
     `ak8PFJets_cfi.py`, `FastjetParameters_cfi.py`,
     `PFJetParameters_cfi.py`, `CaloJetParameters_cfi.py`, and then
     `plugins/VirtualJetProducer.*` and `plugins/FastjetJetProducer.*`.

3. `JetAlgorithms`
   - This contains algorithmic helpers used by producers: boosted-object
     taggers, pruning, subjet filtering, Q-jets, QG likelihood, and fixed-grid
     energy-density calculations.
   - Read this after you understand what the producers are trying to make.

4. `JetAssociationAlgorithms` and `JetAssociationProducers`
   - These connect jets to tracks and vertices. They are important for b
     tagging, pileup rejection, vertex compatibility, and JPT-style workflows.

5. `JetPlusTracks`
   - This is the legacy Jet-Plus-Track correction chain, combining calorimeter
     jets with charged-track information and ZSP corrections.

6. `JetAnalyzers`
   - This package is mostly examples, validation analyzers, ntuple makers, and
     old workbook-style analysis scripts. Use it after the reconstruction chain
     is clear.

7. `FFTJetAlgorithms` and `FFTJetProducers`
   - These implement the older FFTJet pattern-recognition and pileup workflow.
     They are specialized and less central than the standard FastJet-based path.

## Physics Picture

`RecoJets` is the reconstruction layer that builds jet objects from several
constituent types:

- `GenJet`: clustered from selected stable generator particles.
- `CaloJet`: clustered from calorimeter towers.
- `PFJet`: clustered from particle-flow candidates, including CHS/Puppi
  variants for pileup mitigation.
- `PFClusterJet`: clustered from PF calorimeter clusters.
- `TrackJet`: clustered from selected reconstructed tracks.
- `JPTJet`: calorimeter jets corrected with track information.
- Substructure/top-tagged jets: large-R jets with grooming, subjet, and
  boosted-object observables.

The main technical split is:

- `python/*_cfi.py` defines one module or parameter block.
- `python/*_cff.py` composes modules into CMSSW tasks/sequences.
- `plugins/*.cc` are CMSSW framework modules.
- `interface/*.h` and `src/*.cc` are reusable implementation classes.
- `test` and `validation` contain runnable examples, macros, and checks.

## Subpackage Tree

```text
RecoJets/
|-- Configuration/
|   |-- doc/
|   |   |-- WorkBook/
|   |-- python/
|-- FFTJetAlgorithms/
|   |-- interface/
|   |-- src/
|-- FFTJetProducers/
|   |-- interface/
|   |-- plugins/
|   |-- python/
|   |-- src/
|-- JetAlgorithms/
|   |-- doc/
|   |-- interface/
|   |-- src/
|-- JetAnalyzers/
|   |-- doc/
|   |-- interface/
|   |-- python/
|   |-- src/
|   |-- test/
|   |   |-- DijetRatio/
|-- JetAssociationAlgorithms/
|   |-- interface/
|   |-- src/
|-- JetAssociationProducers/
|   |-- interface/
|   |-- python/
|   |-- src/
|   |-- test/
|-- JetPlusTracks/
|   |-- plugins/
|   |-- python/
|   |-- test/
|-- JetProducers/
|   |-- data/
|   |-- doc/
|   |   |-- html/
|   |-- interface/
|   |-- plugins/
|   |-- python/
|   |-- src/
|   |-- test/
|   |-- validation/
```

## Configuration

Purpose: top-level CMSSW reconstruction fragments that assemble jet workflows
from lower-level producers. This is the main map of what runs in RECO/AOD-like
jet reconstruction.

### `Configuration/doc`

- `RecoJets_AOD.doi`
  - Data object inclusion metadata for AOD-level RecoJets products. Use it as a
    historical/packaging reference for what jet data tiers expected to keep.

- `RecoJets_RECO.doi`
  - Data object inclusion metadata for RECO-level RecoJets products. It is a
    packaging companion to the event-content fragments.

### `Configuration/doc/WorkBook`

- `analyzeJets.C`
  - ROOT workbook macro for inspecting jet collections from a file. Useful as a
    minimal example of reading jet branches interactively.

- `analyzeJets_head.C`
  - Header/helper part for the workbook jet analysis macro. It contains setup
    code shared by the interactive ROOT example.

### `Configuration/python`

- `CaloTowersES_cfi.py`
  - EventSetup configuration for calorimeter tower constituents. It configures
    the tower constituent map used when building CaloTowers for jets.

- `CaloTowersRec_cff.py`
  - Standard calo-tower reconstruction sequence. It schedules tower makers with
    and without HO for downstream calo-jet reconstruction.

- `GenJetParticles_cff.py`
  - Defines `InputGenJetsParticleSelector` modules for generator-particle jet
    inputs, including variants excluding neutrinos and excluding muons/neutrinos.
    This is the physics start point for `GenJet` definitions.

- `JetIDProducers_cff.py`
  - Composes calorimeter jet ID producers, currently centered on AK4 CaloJet ID.
    It defines the standard jet-ID task/sequence fragments.

- `RecoCaloTowersGR_cff.py`
  - Global-reconstruction calo-tower sequence. It is a compact GR entry point
    for tower production before calo jets.

- `RecoGenJets_cff.py`
  - Standard generator-level jet sequences. It builds AK4/AK8 GenJets and
    no-neutrino/no-muon variants used for physics matching and truth studies.

- `RecoJPTJetsHIC_cff.py`
  - Heavy-ion JPT jet sequence fragment. It keeps legacy cone-style heavy-ion
    JPT correction paths, with only the iterative-cone path active.

- `RecoJPTJets_cff.py`
  - Standard AK4 Jet-Plus-Track sequence fragment. It schedules the JPT/ZSP
    correction task for anti-kt R=0.4 jets.

- `RecoJetAssociations_cff.py`
  - Standard jet-track association sequence. It composes AK4 JTA tasks and an
    explicit association sequence for track/vertex-based jet workflows.

- `RecoJetsGR_cff.py`
  - Compact global-reconstruction calo-jet sequence. It schedules fixed-grid
    calo rho and AK4 CaloJets.

- `RecoJetsGlobal_cff.py`
  - Main global and high-level jet reconstruction steering fragment. It joins
    calo jets, PF jets, jet IDs, corrections, and associations, with era
    modifiers for heavy-ion running.

- `RecoJets_EventContent_cff.py`
  - Event-content rules for keeping/dropping RecoJets products. Read this when
    debugging why a jet collection appears or disappears in output tiers.

- `RecoJets_cff.py`
  - Standard calo-jet reconstruction fragment. It defines AK4 CaloJets,
    fixed-grid calo rho, all-calo-jet variants, and PU-offset-corrected calo
    jets.

- `RecoPFClusterJets_cff.py`
  - PF-cluster jet reconstruction sequence. It schedules PF cluster candidates
    and AK4 PFClusterJets for calorimeter-cluster-based studies.

- `RecoPFJets_cff.py`
  - Main PF-jet reconstruction fragment. It schedules fixed-grid rho variants,
    AK4 PFJets, AK8 PFJets, CHS/Puppi large-R jets, grooming, and heavy-ion PF
    jet variants.

- `RecoTrackJets_cff.py`
  - Track-jet reconstruction fragment. It selects tracks with vertex references
    and runs AK4 TrackJets.

## FFTJetAlgorithms

Purpose: algorithm helpers for FFTJet, a pattern-recognition approach based on
energy-flow grids, scale-space peaks, and pileup modeling.

### `FFTJetAlgorithms`

- `BuildFile.xml`
  - SCRAM build description for the FFTJet algorithm library. It declares
    dependencies needed by the interface/src implementation files.

### `FFTJetAlgorithms/interface`

- `AbsPileupCalculator.h`
  - Abstract interface for pileup estimators used by FFTJet code. Implemented
    calculators return eta/phi-dependent background information for correction.

- `EtaAndPtDependentPeakSelector.h`
  - Peak-selection functor with eta- and pt-dependent requirements. Used to
    reject FFTJet pattern-recognition peaks outside calibrated acceptance.

- `EtaDependentPileup.h`
  - Pileup model parameterized primarily in eta. It provides background values
    from eta-dependent calibration tables.

- `JetAbsEta.h`
  - Small functors returning absolute eta for FFTJet peaks or reconstructed
    jets. Used for eta-binned selection, sorting, and calibration.

- `JetConvergenceDistance.h`
  - Distance metric for convergence tests between FFTJet reconstructed jets.
    It quantifies whether iterative jet reconstruction has stabilized.

- `JetToPeakDistance.h`
  - Distance calculator between reconstructed jets and FFTJet peaks. Used for
    matching pattern-recognition peaks to final jet candidates.

- `LinInterpolatedTable1D.h`
  - One-dimensional linear interpolation table. FFTJet pileup and calibration
    code use it for smooth lookup of tabulated corrections.

- `LookupTable2d.h`
  - Two-dimensional lookup/interpolation table. Used for eta/pt or eta/phi
    dependent calibration factors.

- `PileupGrid2d.h`
  - Grid representation of pileup density in two dimensions. It supports
    background subtraction and pileup-shape studies in FFTJet workflows.

- `ScaleCalculators.h`
  - Functors that compute scale variables for FFTJet peaks or jets. These are
    used in scale-space clustering and matching decisions.

- `VBuilders.h`
  - Four-vector builder helpers for constructing physics vectors from FFTJet
    ingredients. They define how pt/eta/phi/energy-like quantities become jet
    four-vectors.

- `adjustForPileup.h`
  - Functions that adjust FFTJet candidate kinematics for estimated pileup.
    This is the algorithm-side correction hook.

- `clusteringTreeConverters.h`
  - Conversion utilities between FFTJet clustering trees and persistable CMSSW
    pattern-recognition tree objects.

- `fftjetTypedefs.h`
  - Central typedefs for FFTJet numeric precision, FFT engine, vector type, and
    background functors. Read it before changing FFTJet template code.

- `gridConverters.h`
  - Utilities converting FFTJet grids into CMSSW-storable grid objects and back.
    Used by tree dumps, analyzers, and persistency code.

- `jetConverters.h`
  - Utilities converting FFTJet jets/peaks into reco FFTJet data formats. It
    bridges algorithm objects and EDM products.

- `matchOneToOne.h`
  - Generic one-to-one matching utility using a supplied distance calculator.
    Useful for peak-jet or collection-collection matching with exclusivity.

### `FFTJetAlgorithms/src`

- `EtaAndPtDependentPeakSelector.cc`
  - Implementation of the eta/pt-dependent FFTJet peak selector. It applies
    threshold tables and acceptance logic.

- `EtaDependentPileup.cc`
  - Implementation of eta-dependent pileup lookup and evaluation. It reads and
    evaluates the model used by FFTJet pileup correction.

- `JetConvergenceDistance.cc`
  - Implementation of the FFTJet convergence distance metric. It compares jet
    positions/kinematics for iterative stopping criteria.

- `JetToPeakDistance.cc`
  - Implementation of jet-to-peak matching distance. Used when associating
    scale-space peaks with reconstructed jet candidates.

- `LinInterpolatedTable1D.cc`
  - Implementation of the 1D interpolation table. It handles bin lookup and
    interpolation details for calibration-like data.

- `LookupTable2d.cc`
  - Implementation of the 2D lookup table. It provides interpolation and bounds
    handling for two-variable correction maps.

- `adjustForPileup.cc`
  - Implementation of pileup-adjustment functions. It modifies candidate
    momenta/background quantities using FFTJet pileup estimates.

## FFTJetProducers

Purpose: CMSSW producers/analyzers/filters wrapping FFTJet pattern recognition,
pileup estimation, correction, and diagnostic output.

### `FFTJetProducers`

- `BuildFile.xml`
  - SCRAM build rules for the FFTJet producer support library. It declares
    dependencies for parser/interface classes used by plugins.

### `FFTJetProducers/interface`

- `FFTJetInterface.h`
  - Interface class that coordinates FFTJet grid building, peak finding, and
    jet reconstruction. It is the central bridge from plugin configuration to
    FFTJet algorithms.

- `FFTJetParameterParser.h`
  - Parser utilities for constructing FFTJet algorithm objects from CMSSW
    parameter sets. This file is essential for understanding FFTJet python
    configuration semantics.

- `JetType.h`
  - Jet-type helper used by FFTJet producer code. It maps requested output jet
    categories to concrete data formats.

### `FFTJetProducers/plugins`

- `BuildFile.xml`
  - SCRAM plugin build rules for FFTJet framework modules.

- `FFTJetCorrectionProducer.cc`
  - EDProducer applying FFTJet correction sequences to FFTJet jets. It reads
    uncorrected FFTJet products and emits corrected jet collections.

- `FFTJetDijetFilter.cc`
  - EDFilter selecting events with FFTJet dijet-like pattern-recognition
    topology. It is useful for specialized FFTJet studies and skims.

- `FFTJetEFlowSmoother.cc`
  - EDProducer that builds/smooths energy-flow histograms on FFTJet grids. It is
    an early stage of FFTJet pattern recognition.

- `FFTJetPFPileupCleaner.cc`
  - EDProducer cleaning PF candidates using FFTJet pileup information. It links
    FFTJet pileup estimates to PF-candidate-level mitigation.

- `FFTJetPatRecoProducer.cc`
  - EDProducer running FFTJet pattern recognition. It creates peaks, trees, and
    grid-like outputs from calorimeter or PF inputs.

- `FFTJetPileupEstimator.cc`
  - EDProducer summarizing pileup estimates from FFTJet pileup histograms. It
    produces event-level quantities for later correction/analyzer stages.

- `FFTJetPileupProcessor.cc`
  - EDProducer processing pileup histograms/grids for calibration and studies.
    It prepares FFTJet pileup products used by estimators and analyzers.

- `FFTJetProducer.cc`
  - EDProducer that runs the FFTJet jet reconstruction itself. It produces jet
    collections from FFTJet pattern-recognition outputs.

- `FFTJetProducer.h`
  - Header for the FFTJet jet producer plugin. It declares framework tokens,
    configuration, and reconstruction helper methods.

- `FFTJetTreeDump.cc`
  - EDAnalyzer dumping FFTJet pattern-recognition trees. Use it for debugging
    FFTJet peak/tree internals.

- `FFTJetVertexAdder.cc`
  - EDProducer adding or modifying vertex information for FFTJet pileup studies.
    It can create "fudged" vertex collections for calibration workflows.

### `FFTJetProducers/python`

- `fftjetcommon_cfi.py`
  - Shared FFTJet parameter blocks: grids, kernels, peak selectors, clustering,
    pileup, and calibration settings. Start here before reading specific FFTJet
    module configs.

- `fftjetcorrectionproducer_cfi.py`
  - Helper for building `FFTJetCorrectionProducer` configurations. It wires a
    jet producer label to the requested correction sequence.

- `fftjetdijetfilter_cfi.py`
  - Default configuration for the FFTJet dijet filter. It selects on FFTJet
    pattern-recognition tree content.

- `fftjeteflowsmoother_cfi.py`
  - Default configuration for FFTJet energy-flow smoothing. It chooses input
    towers, grids, kernels, and primary-vertex handling.

- `fftjetpatrecoproducer_cfi.py`
  - Default FFTJet pattern-recognition configuration. It defines peak finding,
    clustering tree production, grids, and event-shape controls.

- `fftjetpfpileupcleaner_cfi.py`
  - Default PF pileup cleaner configuration driven by FFTJet products. It links
    PF candidates, vertices, and fake/estimated pileup vertices.

- `fftjetpileupestimator_calo_cfi.py`
  - Calo-mode calibrated FFTJet pileup estimator configuration. It reads calo
    pileup processor output and emits calibrated pileup summaries.

- `fftjetpileupestimator_calo_uncalib_cfi.py`
  - Calo-mode uncalibrated pileup estimator configuration. Useful for deriving
    or checking calibration constants.

- `fftjetpileupestimator_pf_cfi.py`
  - PF-mode calibrated FFTJet pileup estimator configuration. It is the PF
    analogue of the calo estimator.

- `fftjetpileupestimator_pf_uncalib_cfi.py`
  - PF-mode uncalibrated pileup estimator configuration. Used in FFTJet pileup
    calibration and MC studies.

- `fftjetpileupprocessor_caloprod_cfi.py`
  - Calo production-mode pileup processor configuration. It prepares pileup
    histograms/products for standard FFTJet calo workflows.

- `fftjetpileupprocessor_calostudy_cfi.py`
  - Calo study-mode pileup processor configuration. It keeps more diagnostic
    information for calibration/validation.

- `fftjetpileupprocessor_pfprod_cfi.py`
  - PF production-mode pileup processor configuration. It prepares PF pileup
    products for FFTJet estimators.

- `fftjetpileupprocessor_pfprod_clean_cfi.py`
  - PF production-mode processor configured for cleaned PF inputs. It supports
    workflows where PF pileup candidates have already been mitigated.

- `fftjetpileupprocessor_pfstudy_cfi.py`
  - PF study-mode pileup processor configuration. It enables richer diagnostic
    output for MC/data comparisons.

- `fftjetproducer_cfi.py`
  - Default FFTJet jet producer configuration. It wires FFTJet pattern
    recognition, pileup, and output jet-type settings.

- `fftjettreedump_cfi.py`
  - Configuration for dumping FFTJet clustering trees. Use it when debugging
    peak/tree structure.

- `fftjetvertexadder_cfi.py`
  - Configuration for the FFTJet vertex adder. It sets beam spot, vertex input,
    and fake-vertex output labels.

- `mixed_calib_calo_ttbar_result.py`
  - Generated/derived mixed calibration constants for calo FFTJet ttbar studies.
    Treat as calibration payload-like python data.

- `mixed_calib_pf_ttbar_result.py`
  - Generated/derived mixed calibration constants for PF FFTJet ttbar studies.
    Treat as calibration payload-like python data.

- `pileup_calib_calo_cfi.py`
  - Calo FFTJet pileup calibration parameter data. It configures pileup
    correction lookup values.

- `pileup_calib_pf_cfi.py`
  - PF FFTJet pileup calibration parameter data. It configures PF pileup
    correction lookup values.

- `pileup_shape_Fall10_L1Hybrid_AK5Calo_v1_cfi.py`
  - Era/sample-specific FFTJet pileup eta-shape constants for AK5 CaloJets. Used
    by old L1Hybrid-style studies.

- `pileup_shape_Fall10_L1Hybrid_AK5PF_v1_cfi.py`
  - Era/sample-specific FFTJet pileup eta-shape constants for AK5 PFJets.

- `pileup_shape_Summer11_Calo_v1_cfi.py`
  - Summer11 calo pileup-shape constants for FFTJet. It is generated calibration
    data, not executable logic.

- `pileup_shape_Summer11_PF_Clean_v1_cfi.py`
  - Summer11 PF-cleaned pileup-shape constants for FFTJet.

- `pileup_shape_Summer11_PF_v1_cfi.py`
  - Summer11 PF pileup-shape constants for FFTJet.

### `FFTJetProducers/src`

- `FFTJetInterface.cc`
  - Implementation of the main FFTJet interface class. It orchestrates grids,
    smoothing, clustering, and jet conversion.

- `FFTJetParameterParser.cc`
  - Implementation of the parameter parser. It constructs FFTJet grids, kernels,
    selectors, pileup calculators, and correction functors from python configs.

- `JetType.cc`
  - Implementation of FFTJet jet-type helper logic. It maps configured type
    strings/enums to output behavior.

## JetAlgorithms

Purpose: reusable jet algorithm and substructure code, mostly independent of
CMSSW framework modules. Producers call these classes to do physics work.

### `JetAlgorithms`

- `BuildFile.xml`
  - SCRAM build rules for the algorithm library.

### `JetAlgorithms/doc`

- `JetAlgorithms.doc`
  - Doxygen-era package description. It states that this package provides jet
    clustering algorithms, external wrappers, and tools for jet-object creation.

### `JetAlgorithms/interface`

- `CATopJetAlgorithm.h`
  - CMS Cambridge-Aachen top-tagging algorithm interface. It handles subjet
    decomposition and top-candidate selection.

- `CATopJetHelper.h`
  - Helper functions/classes for CA top-jet algorithms. It supports subjet and
    candidate manipulation.

- `CMSBoostedTauSeedingAlgorithm.h`
  - Boosted-tau subjet seeding algorithm. It selects subjet structures suitable
    as tau seeds inside large-radius jets.

- `CMSInsideOutAlgorithm.h`
  - Interface for the CMS inside-out jet algorithm. It supports a specialized
    clustering/reclustering strategy used by `CMSInsideOutJetProducer`.

- `CMSTopTagger.h`
  - Top-tagging helper definitions for CMS-style top tagging. It collects
    common top-tagger structures.

- `CompoundPseudoJet.h`
  - FastJet `PseudoJet` extension/helper carrying compound jet information. Used
    when constituent or subjet structure must survive algorithm steps.

- `FastPrunePlugin.hh`
  - FastJet plugin implementing pruning during clustering. It removes soft,
    wide-angle recombinations according to pruning criteria.

- `FixedGridEnergyDensity.h`
  - Fixed eta/phi grid energy-density calculator. Used for rho-like pileup/UE
    estimates.

- `HEPTopTaggerV2.h`
  - HEPTopTagger v2 implementation interface. It identifies boosted hadronic
    top candidates using mass-drop/filtering logic.

- `HEPTopTaggerWrapperV2.h`
  - Wrapper around HEPTopTagger v2 for CMSSW/FastJet integration. Producers use
    it to run the algorithm with configured parameters.

- `JetAlgoHelper.h`
  - General helper utilities for jet algorithms. It contains common kinematic
    and constituent-manipulation support.

- `PrunedRecombiner.hh`
  - FastJet recombiner implementing pruning behavior. It is used with FastJet
    clustering definitions for groomed jets.

- `QGLikelihoodCalculator.h`
  - Quark-gluon likelihood calculator interface. It evaluates likelihoods from
    multiplicity, ptD, axis variables, and calibration objects.

- `Qjets.h`
  - Q-jets stochastic clustering algorithm implementation interface. It samples
    clustering histories for volatility/substructure observables.

- `QjetsPlugin.h`
  - FastJet plugin wrapper for Q-jets. It lets Q-jets run through FastJet-style
    clustering APIs.

- `SubJetAlgorithm.h`
  - Subjet production algorithm interface. It handles reclustering/grooming of
    jet constituents into subjet collections.

- `SubjetFilterAlgorithm.h`
  - Filtering algorithm for subjet-based jet production. It removes soft
    substructure according to configured algorithm/R/threshold settings.

### `JetAlgorithms/src`

- `CATopJetAlgorithm.cc`
  - Implementation of the CMS CA top-tagging algorithm. It applies adjacency,
    subjet pt-fraction, eta, and event-scale dependent cuts.

- `CATopJetHelper.cc`
  - Implementation of helper logic for top-jet algorithms. It sorts/selects
    constituents and subjets.

- `CMSBoostedTauSeedingAlgorithm.cc`
  - Implementation of boosted tau seeding from large-radius jet substructure.

- `CMSInsideOutAlgorithm.cc`
  - Implementation of the inside-out clustering algorithm. It is used by the
    corresponding producer for specialized jet finding.

- `FastPrunePlugin.cc`
  - Implementation of the FastJet pruning plugin. It controls when
    recombinations are vetoed as soft/wide-angle.

- `FixedGridEnergyDensity.cc`
  - Implementation of fixed-grid energy-density calculation. It fills grid
    cells and derives rho-like density estimates.

- `HEPTopTaggerV2.cc`
  - Implementation of HEPTopTagger v2 top-candidate selection and filtering.

- `HEPTopTaggerWrapperV2.cc`
  - Wrapper implementation connecting CMSSW producer settings to HEPTopTagger
    v2 internals.

- `PrunedRecombiner.cc`
  - Implementation of the pruning recombiner. It builds pruned four-vectors
    during FastJet clustering.

- `QGLikelihoodCalculator.cc`
  - Implementation of quark-gluon likelihood evaluation from input variables
    and calibration histograms/objects.

- `Qjets.cc`
  - Implementation of stochastic Q-jets clustering. It creates random clustering
    histories for jet substructure studies.

- `QjetsPlugin.cc`
  - Implementation of the FastJet plugin wrapper for Q-jets.

- `SubJetAlgorithm.cc`
  - Implementation of subjet production and reclustering. It supports groomed
    and ungroomed subjet workflows.

- `SubjetFilterAlgorithm.cc`
  - Implementation of subjet filtering. It applies filtering thresholds and
    constructs filtered jet/subjet outputs.

## JetAnalyzers

Purpose: analysis examples, validation analyzers, filters, and old workbook
macros. This is not the core reconstruction path.

### `JetAnalyzers`

- `BuildFile.xml`
  - SCRAM build rules for analyzer plugins and examples.

### `JetAnalyzers/doc`

- `JetAnalyzers.doc`
  - Doxygen package description. It explains that the package provides examples
    and user-contributed analysis code rather than supported analysis utilities.

### `JetAnalyzers/interface`

- `CaloTowersExample.h`
  - Analyzer interface for a simple CaloTower access example. It demonstrates
    reading tower collections.

- `DijetMass.h`
  - Analyzer interface for dijet mass studies. It supports CaloJet, PFJet, and
    GenJet mass plotting examples.

- `DijetRatio.h`
  - Analyzer interface for dijet angular/mass ratio studies. Used by older
    dijet analysis examples.

- `JetAnaPythia.h`
  - Analyzer interface for generator/Pythia jet studies. It provides Calo, PF,
    and GenJet analyzer variants.

- `JetCorExample.h`
  - Header for jet-correction example analyzers. It demonstrates reading
    corrected jet collections.

- `JetPlotsExample.h`
  - Header for simple jet plotting examples. It defines analyzers that fill
    basic kinematic histograms.

- `JetToDigiDump.h`
  - Header for a debugging analyzer that walks from jets to towers, rechits, and
    digis. Useful when debugging detector-level jet inputs.

- `JetValidation.h`
  - Validation analyzer interface for comparing reconstructed jet quantities.
    It is aimed at release/algorithm validation.

- `SimpleJetDump.h`
  - Header for a simple text dump analyzer for jet collections.

- `myFastSimVal.h`
  - Interface for a large FastSim validation analyzer. It is specialized legacy
    validation code.

- `myRawAna.h`
  - Interface for raw-data-oriented jet/tower analyzer code. It is legacy
    diagnostic code.

### `JetAnalyzers/python`

- `QCD_GenJets_cfi.py`
  - PoolSource fragment listing old QCD GenJet samples. It is sample steering
    data for examples, not reconstruction logic.

- `QCDgen_cfi.py`
  - PoolSource fragment listing old QCD generator-level samples. Used by example
    analyzer jobs.

- `RelValQCD_Pt_80_120_cfi.py`
  - PoolSource fragment for an old QCD relval sample. Useful only as a
    historical example input list.

- `fftjetimagerecorder_cfi.py`
  - Configuration for `FFTJetImageRecorder`. It records histograms produced by
    FFTJet energy-flow smoothing.

- `fftjetpileupanalyzer_cfi.py`
  - Configuration for `FFTJetPileupAnalyzer`. It controls which FFTJet pileup
    histograms, summaries, grids, vertices, and rho values are collected.

### `JetAnalyzers/src`

- `CaloTowersExample.cc`
  - Implementation of the simple CaloTower analyzer. It demonstrates reading
    and plotting tower quantities.

- `DijetMass.cc`
  - Implementation of dijet mass analyzers. It fills mass spectra and event
    selection quantities for CaloJet/PFJet/GenJet examples.

- `DijetRatio.cc`
  - Implementation of dijet ratio analysis logic. It supports older QCD angular
    distribution studies.

- `FFTJetImageRecorder.cc`
  - Analyzer implementation that records FFTJet image/grid histograms. Use it
    for inspecting FFTJet energy-flow smoothing output.

- `FFTJetPileupAnalyzer.cc`
  - Analyzer implementation for FFTJet pileup studies. It collects pileup
    summaries, MC pileup info, grids, and optional FastJet rho comparisons.

- `JPTJetSelector.cc`
  - Simple selector module for JPT jets. It filters a JPT collection according
    to configured cuts.

- `JetAnaPythia.cc`
  - Implementation of Calo/Gen/PF jet analyzers for Pythia-style samples. It
    fills event and jet-level histograms.

- `JetIdSelector.cc`
  - Selector/filter implementation based on jet ID information. It is a utility
    for examples that need ID-cleaned jets.

- `JetPlotsExample.cc`
  - Implementation of simple jet-plot analyzers. It is the workbook-style first
    example for plotting jet kinematics.

- `JetToDigiDump.cc`
  - Implementation of the jet-to-digi dump utility. It traces jet constituents
    back through detector objects for debugging.

- `JetValidation.cc`
  - Implementation of jet validation histograms. It compares reconstructed jets
    in validation-style workflows.

- `SimpleJetDump.cc`
  - Implementation of a simple jet dump module. It prints CaloJet/GenJet
    content for debugging.

- `myFastSimVal.cc`
  - Large legacy FastSim validation analyzer. It studies many reconstructed and
    simulated quantities in one module.

- `myRawAna.cc`
  - Legacy raw-data/tower analyzer implementation. It is mainly diagnostic.

- `ptHatFilter.cc`
  - EDFilter using `genEventScale` to filter events by generator pt-hat. It is
    used to prepare QCD samples for analyzer examples.

### `JetAnalyzers/test`

- `CMSDASmacro.c`
  - ROOT macro from CMSDAS-style training material. It demonstrates plotting
    jet-analysis output.

- `DijetMassPlotExample_cfg.py`
  - Example CMSSW job for the dijet mass analyzers. It configures Calo/PF/Gen
    dijet mass plots.

- `DijetMassQstar.cint`
  - ROOT/CINT macro for Q* dijet mass plotting. It is an old analysis-display
    helper.

- `DijetMassZprime.cint`
  - ROOT/CINT macro for Z' dijet mass plotting. It is an old analysis-display
    helper.

- `DijetRatioPlotExample_cfg.py`
  - Example CMSSW job for the dijet ratio analyzer. It configures inputs and
    analyzer settings for ratio plots.

- `DrawJetValidation.C`
  - ROOT macro for drawing jet validation histograms. Use after running
    validation-style analyzer jobs.

- `GenJetAna.py`
  - Example job running the GenJet analyzer. It demonstrates generator-level jet
    access and plotting.

- `JetAnaPythia.py`
  - Example job for Pythia jet analyzers. It configures Calo/Gen/PF analyzer
    variants.

- `JetCorrectionUncertaintyExample.py`
  - Example job demonstrating jet-correction uncertainty access. It is useful
    when learning how corrected jets are inspected.

- `JetPlotsExample.py`
  - Minimal example job for basic jet plots. It is one of the simplest analyzer
    entry points.

- `JetValidation.py`
  - Example job for the `JetValidation` analyzer. It sets up validation-style
    histograms.

- `cruzet4.py`
  - Example/legacy configuration for cosmic-run-style jet/tower analysis.

- `dumpFFTJetGrids.py`
  - Example job dumping FFTJet grids/trees. It is useful for FFTJet debugging.

- `ptHatFilter.py`
  - Example configuration for the pt-hat filter. It demonstrates generator-scale
    event filtering.

- `runCMSDAS11DijetAnalyzer.py`
  - CMSDAS-era dijet analyzer job. It is a training/example workflow.

- `runFFTJetPileupAnalyzerCaloCalibTemplate.py`
  - Template job for calo FFTJet pileup calibration analysis.

- `runFFTJetPileupAnalyzerCaloProdTemplate.py`
  - Template job for calo FFTJet pileup production-mode analysis.

- `runFFTJetPileupAnalyzerCaloStudyTemplate.py`
  - Template job for calo FFTJet pileup study-mode analysis.

- `runFFTJetPileupAnalyzerPFCalibTemplate.py`
  - Template job for PF FFTJet pileup calibration analysis.

- `runFFTJetPileupAnalyzerPFProdTemplate.py`
  - Template job for PF FFTJet pileup production-mode analysis.

- `runFFTJetPileupAnalyzerPFStudyTemplate.py`
  - Template job for PF FFTJet pileup study-mode analysis.

- `runL2L3JetCorrectionExample_cfg.py`
  - Example applying L2L3 jet corrections and plotting corrected jets.

- `runL2L3L4JetCorrectionExample_cfg.py`
  - Example applying L2L3L4 corrections. It demonstrates extra correction-level
    handling in analyzer jobs.

- `runL2L3L5JetCorrectionExample_cfg.py`
  - Example applying L2L3L5 flavor-style corrections.

- `runL2L3L5L7JetCorrectionExample_cfg.py`
  - Example applying L2L3L5L7 corrections in one chain.

- `runL2L3L7JetCorrectionExample_cfg.py`
  - Example applying L2L3L7 corrections.

### `JetAnalyzers/test/DijetRatio`

- `MassAnaBackgrd.C`
  - ROOT macro for dijet-ratio background mass analysis.

- `condor-submit-diJetAnalysis.csh`
  - Condor submission helper for the old dijet analysis workflow.

- `datasetBackgrd.txt`
  - Dataset list for the dijet background workflow.

- `job-submission`
  - Submission helper/script for dijet-ratio jobs.

- `moving.csh`
  - Shell helper for moving outputs in the dijet analysis workflow.

- `submitDiJetAnalysis.csh`
  - Shell submission script for dijet analysis jobs.

## JetAssociationAlgorithms

Purpose: pure algorithm classes that associate tracks to jets at the vertex or
calorimeter face and estimate vertex compatibility.

### `JetAssociationAlgorithms`

- `BuildFile.xml`
  - SCRAM build rules for the association algorithm library.

### `JetAssociationAlgorithms/interface`

- `JetSignalVertexCompatibilityAlgo.h`
  - Algorithm interface for jet-signal-vertex compatibility. It evaluates how
    compatible jet-associated tracks are with vertices.

- `JetTracksAssociationDR.h`
  - Base delta-R jet-track association algorithm. It matches tracks to jets in
    angular space.

- `JetTracksAssociationDRCalo.h`
  - Delta-R association at the calorimeter face. It is used when tracks are
    extrapolated outward before matching to calorimeter jets.

- `JetTracksAssociationDRVertex.h`
  - Delta-R association at the primary vertex. It matches tracks to jet axes at
    vertex position.

- `JetTracksAssociationDRVertexAssigned.h`
  - Vertex-assigned variant of the delta-R association algorithm. It accounts
    for vertex assignment when associating tracks.

- `JetTracksAssociationExplicit.h`
  - Explicit association algorithm interface. It builds associations from
    already-linked jet/track information.

- `JetTracksAssociationXtrpCalo.h`
  - Track-extrapolation-to-calo association interface. It supports matching
    tracks to calorimeter-surface positions.

### `JetAssociationAlgorithms/src`

- `JetSignalVertexCompatibilityAlgo.cc`
  - Implementation of vertex-compatibility calculations for jet-associated
    tracks.

- `JetTracksAssociationDR.cc`
  - Implementation of generic delta-R association logic.

- `JetTracksAssociationDRCalo.cc`
  - Implementation of delta-R matching at the calorimeter face.

- `JetTracksAssociationDRVertex.cc`
  - Implementation of delta-R matching at the vertex.

- `JetTracksAssociationDRVertexAssigned.cc`
  - Implementation of the vertex-assigned association variant.

- `JetTracksAssociationExplicit.cc`
  - Implementation of explicit association construction.

- `JetTracksAssociationXtrpCalo.cc`
  - Implementation of track extrapolation and matching to calo-face positions.

## JetAssociationProducers

Purpose: CMSSW modules and python fragments that run the association algorithms
and write `JetTracksAssociation`, extended-jet, and vertex-compatibility
products.

### `JetAssociationProducers`

- `BuildFile.xml`
  - SCRAM build rules for jet association producer modules.

### `JetAssociationProducers/interface`

- `TrackExtrapolator.h`
  - Helper interface for extrapolating tracks to detector surfaces. Used by
    calo-face jet-track association modules.

### `JetAssociationProducers/python`

- `ak4JTA_cff.py`
  - Standard AK4 jet-track association task. It configures vertex and calo-face
    association for AK4 jets.

- `ak5JTA_cff.py`
  - Legacy AK5 jet-track association task. Kept for compatibility with older
    AK5 workflows.

- `ak7JTA_cff.py`
  - Legacy AK7 jet-track association task. Used by older large-R studies.

- `ic5JetTracksAssociatorAtVertex_cfi.py`
  - Iterative-cone R=0.5 jet-track association at the vertex.

- `ic5JetVertexCompatibility_cfi.py`
  - Iterative-cone R=0.5 jet vertex-compatibility configuration.

- `ic5PFJetTracksAssociatorAtVertex_cfi.py`
  - Iterative-cone PF-jet association at the vertex.

- `iterativeCone5JTA_cff.py`
  - Legacy iterative-cone R=0.5 JTA sequence.

- `j2tParametersCALO_cfi.py`
  - Shared parameters for jet-to-track association at the calorimeter face.

- `j2tParametersVX_cfi.py`
  - Shared parameters for jet-to-track association at the vertex.

- `jvcParameters_cfi.py`
  - Shared parameters for jet-vertex compatibility calculations.

- `kt4JTA_cff.py`
  - Legacy kt R=0.4 JTA sequence.

- `midPointCone5JTA_cff.py`
  - Legacy midpoint-cone R=0.5 JTA sequence.

- `sisCone5JTA_cff.py`
  - Legacy SISCone R=0.5 JTA sequence.

- `trackExtrapolator_cfi.py`
  - Configuration for the track extrapolator helper.

### `JetAssociationProducers/src`

- `JetExtender.cc`
  - Producer implementation that extends jets with associated-track
    information.

- `JetExtender.h`
  - Header for the jet extender producer.

- `JetSignalVertexCompatibility.cc`
  - Producer implementation for jet signal-vertex compatibility products.

- `JetSignalVertexCompatibility.h`
  - Header for the vertex-compatibility producer.

- `JetTracksAssociatorAtCaloFace.cc`
  - Producer implementation associating extrapolated tracks to jets at the
    calorimeter face.

- `JetTracksAssociatorAtCaloFace.h`
  - Header for calo-face jet-track association producer.

- `JetTracksAssociatorAtVertex.cc`
  - Producer implementation associating tracks to jets at the vertex.

- `JetTracksAssociatorAtVertex.h`
  - Header for vertex jet-track association producer.

- `JetTracksAssociatorExplicit.cc`
  - Producer implementation for explicit jet-track associations.

- `JetTracksAssociatorExplicit.h`
  - Header for explicit association producer.

- `SealModule.cc`
  - Plugin registration file for association producer modules.

- `TrackExtrapolator.cc`
  - Implementation of track extrapolation helper logic.

### `JetAssociationProducers/test`

- `BuildFile.xml`
  - Build rules for association producer test plugins.

- `PileupJetAnalyzer.cc`
  - Test analyzer for studying pileup jets with association information.

- `dumpJTA.C`
  - ROOT macro for dumping/inspecting jet-track association products.

- `pileupJetAnalysis_mkplots.C`
  - ROOT plotting macro for pileup jet analysis outputs.

## JetPlusTracks

Purpose: legacy Jet-Plus-Track correction modules. These correct calorimeter
jets using charged tracks and ZSP corrections.

### `JetPlusTracks/plugins`

- `BuildFile.xml`
  - SCRAM plugin build rules for JPT modules.

- `JetPlusTrackAddonSeedProducer.cc`
  - Producer creating extra seeds or associations needed by Jet-Plus-Track
    correction workflows.

- `JetPlusTrackCorrector.cc`
  - Implementation of the main JPT corrector. It applies track-based corrections
    to calorimeter jets.

- `JetPlusTrackCorrector.h`
  - Header for the main JPT corrector.

- `JetPlusTrackProducer.cc`
  - EDProducer building JPT jet collections from calo jets, tracks, and
    correction information.

- `JetPlusTrackProducer.h`
  - Header for the standard JPT producer.

- `JetPlusTrackProducerAA.cc`
  - Heavy-ion/AA variant of the JPT producer implementation.

- `JetPlusTrackProducerAA.h`
  - Header for the heavy-ion JPT producer.

- `SealModule.cc`
  - Plugin registration file for JPT modules.

- `SimpleZSPJPTJetCorrector.cc`
  - Simpler ZSP correction implementation for JPT jets. It applies
    zero-suppression-style calorimeter corrections.

- `SimpleZSPJPTJetCorrector.h`
  - Header for the simple ZSP JPT corrector.

- `ZSPJPTJetCorrector.cc`
  - Full ZSP JPT corrector implementation. It handles detailed calorimeter
    response corrections used before/with track corrections.

- `ZSPJPTJetCorrector.h`
  - Header for the full ZSP JPT corrector.

### `JetPlusTracks/python`

- `JetPlusTrackCorrectionsAA_cff.py`
  - Heavy-ion Jet-Plus-Track correction sequence.

- `JetPlusTrackCorrections_cff.py`
  - Standard JPT correction sequence. It composes ZSP and track-based
    corrections for AK4-style workflows.

- `JetPlusTrackCorrections_cfi.py`
  - Parameter blocks for JPT/ZSP correctors. It defines track quality,
    calorimeter matching, and correction settings.

- `PATJetPlusTrackCorrections_cff.py`
  - PAT-oriented JPT correction sequence. It adapts JPT corrections for PAT jet
    workflows.

- `ZSPJetCorrections332_cff.py`
  - Legacy ZSP correction producers for old IC5/SISCone/AK5 calo jets. Kept for
    backward compatibility.

### `JetPlusTracks/test`

- `JetShapeJPTAnalysis_mc_s_sql_qcd_pat2.py`
  - Example analysis job for JPT jet shapes in QCD/PAT samples.

## JetProducers

Purpose: central reconstruction package for producing jet collections and
jet-level observables.

### `JetProducers`

- `BuildFile.xml`
  - SCRAM build rules for the main jet producer library and plugins.

### `JetProducers/data`

- `download.url`
  - Data download pointer for external payload files used by this package, such
    as TMVA weights for pileup jet ID.

### `JetProducers/doc/html`

- `jetSimuChain.html`
  - Historical HTML tutorial describing generator, simulation, calorimeter
    reconstruction, CaloTower production, and jet reconstruction chain.

### `JetProducers/interface`

- `AnomalousTower.h`
  - Helper class for tracking anomalous calorimeter tower content. Used by
    CaloJet ID and cleaning-related calculations.

- `BackgroundEstimator.h`
  - Interface for background estimation used by pileup/underlying-event
    subtraction algorithms.

- `CastorJetIDHelper.h`
  - Helper class for CASTOR jet ID calculations.

- `ECFAdder.h`
  - EDProducer interface for energy-correlation-function observables. Used for
    boosted-jet substructure variables.

- `JetIDHelper.h`
  - Helper class computing calorimeter jet ID quantities from towers/rechits.

- `JetMatchingTools.h`
  - Utility functions for matching jet collections. Used for association and
    validation-style workflows.

- `JetMuonHitsIDHelper.h`
  - Helper for identifying muon-hit-related jet ID quantities. It contributes
    to specialized jet cleaning diagnostics.

- `JetSpecific.h`
  - Utilities for filling jet-type-specific quantities in reconstructed jet
    objects.

- `MVAJetPuId.h`
  - Main algorithm class for MVA pileup jet ID variables and discriminator
    evaluation.

- `NjettinessAdder.h`
  - EDProducer interface for N-subjettiness value-map production.

- `PileUpSubtractor.h`
  - Helper class for subtracting pileup/underlying event from jets.

- `PileupJPTJetIdAlgo.h`
  - Algorithm class for pileup ID on JPT jets.

- `PileupJetIdAlgo.h`
  - Algorithm class for pileup jet ID variable calculation and MVA/cut-based ID.

- `QGTagger.h`
  - EDProducer interface for quark-gluon tagging value maps.

- `QjetsAdder.h`
  - EDProducer interface for Q-jets volatility/substructure value maps.

- `VirtualJetProducerHelper.h`
  - Helper templates and utilities shared by virtual/fastjet producers when
    translating constituents into jet objects.

### `JetProducers/plugins`

- `BasicToPFJet.cc`
  - EDProducer converting `BasicJet` collections into `PFJet` collections. Used
    when algorithms produce basic jets but downstream code expects PF jets.

- `BasicToPFJet.h`
  - Header for the BasicJet-to-PFJet converter.

- `BetaStarVarProducer.cc`
  - Producer of charged-from-primary-vertex energy fraction value maps for PAT
    jets. It supports beta/beta-star-like pileup observables.

- `BoostedTauSeedsProducer.cc`
  - Producer building boosted-tau seeds from subjets and PF candidates. It has
    reco and PAT variants.

- `BuildFile.xml`
  - SCRAM plugin build rules for main jet producer modules.

- `CATopJetProducer.cc`
  - Producer implementation for CMS CA top jets. It runs standard jet
    clustering and then applies CA top-tagging/subjet logic.

- `CATopJetProducer.h`
  - Header for the CA top-jet producer.

- `CATopJetTagger.cc`
  - Producer implementation that creates top-tagging information from CA top
    jets.

- `CATopJetTagger.h`
  - Header for the CA top-tag information producer.

- `CMSInsideOutJetProducer.cc`
  - Producer implementation for inside-out jet clustering.

- `CMSInsideOutJetProducer.h`
  - Header for the inside-out jet producer.

- `CSJetProducer.cc`
  - Producer implementing constituent subtraction using FastJet contrib. It is
    a pileup mitigation path for PF jets.

- `CSJetProducer.h`
  - Header for the constituent-subtraction jet producer.

- `CastorJetIDProducer.cc`
  - Producer creating CASTOR jet ID information.

- `CastorJetIDProducer.h`
  - Header for the CASTOR jet ID producer.

- `CompoundJetProducer.cc`
  - Producer for compound/substructure-aware jet outputs. It reuses the virtual
    jet producer infrastructure.

- `CompoundJetProducer.h`
  - Header for the compound jet producer.

- `ECFAdder.cc`
  - Implementation of energy-correlation-function value-map production. It adds
    ECF/C/D/M/N/U-style substructure observables.

- `FastjetJetProducer.cc`
  - Main FastJet-based producer implementation. It clusters constituents using
    anti-kt, kt, Cambridge-Aachen, cone plugins, area/rho options, grooming, and
    jet-type filling.

- `FastjetJetProducer.h`
  - Header for the FastJet jet producer and dynamic filtering helpers.

- `FixedGridRhoProducer.cc`
  - Producer computing fixed-grid rho from reco candidates. Used for pileup/UE
    density estimates.

- `FixedGridRhoProducer.h`
  - Header for the fixed-grid rho producer.

- `FixedGridRhoProducerFastjet.cc`
  - FastJet-based fixed-grid rho producer implementation.

- `FixedGridRhoProducerFastjetFromRecHit.cc`
  - Fixed-grid rho producer reading ECAL/HCAL rechits directly. Used mainly in
    HLT-like rechit workflows.

- `HFJetShowerShape.cc`
  - Producer computing HF jet shower-shape variables from jets and vertices.
    These variables help reject noise or noncollision backgrounds.

- `HTTTopJetProducer.cc`
  - Producer implementation for HEPTopTagger-based top jets.

- `HTTTopJetProducer.h`
  - Header for the HEPTopTagger top-jet producer.

- `InputGenJetsParticleSelector.cc`
  - Producer selecting stable generator particles for GenJet clustering,
    including configurable exclusions for neutrinos and muons.

- `InputGenJetsParticleSelector.h`
  - Header for the generator-particle selector.

- `JetIDProducer.cc`
  - Producer computing CaloJet ID objects from calo jets and rechits.

- `JetIDProducer.h`
  - Header for the CaloJet ID producer.

- `JetMatcherDR.cc`
  - Producer creating one-to-one delta-R jet matching association maps between
    two jet collections.

- `MVAJetPuIdProducer.cc`
  - Producer running MVA pileup jet ID and producing discriminator/id value
    maps.

- `NjettinessAdder.cc`
  - Producer computing N-subjettiness (`tau1`, `tau2`, `tau3`, etc.) value maps
    for jet collections.

- `PUFilter.cc`
  - Producer/filter-like module applying pileup jet ID decisions to PF jets. It
    is used in HLT-style workflows.

- `PileupJPTJetIdProducer.cc`
  - Producer running pileup ID for JPT jets.

- `PileupJetIdProducer.cc`
  - Producer running the standard pileup jet ID algorithm. It reads jets,
    vertices, rho, optional jet ID, and TMVA payloads.

- `PileupJetIdProducer.h`
  - Header/cache definitions for the pileup jet ID producer and GBR forest
    constants.

- `PtMinJetSelector.cc`
  - Plugin registrations for simple pt-min selectors for Calo, Gen, PF, and
    Basic jets.

- `PtMinJetSelector.h`
  - Header defining the pt-min selector typedefs.

- `QGTagger.cc`
  - Producer computing quark-gluon likelihood and related variables such as
    multiplicity, ptD, and axis observables.

- `QjetsAdder.cc`
  - Producer computing Q-jets observables, especially volatility, for jet
    collections.

- `SubEventGenJetProducer.cc`
  - Producer building GenJets for subevents, useful in pileup/embedded event
    contexts.

- `SubEventGenJetProducer.h`
  - Header for subevent GenJet production.

- `SubJetProducer.cc`
  - Producer creating subjet collections from larger jets or constituents.

- `SubJetProducer.h`
  - Header for the subjet producer.

- `SubjetFilterJetProducer.cc`
  - Producer building filtered jets using subjet filtering logic.

- `SubjetFilterJetProducer.h`
  - Header for the subjet-filter jet producer.

- `VirtualJetProducer.cc`
  - Base implementation for many jet producers. It owns common parameter
    parsing, FastJet setup, constituent handling, area/rho, pileup offset, and
    output filling.

- `VirtualJetProducer.h`
  - Header for the base virtual jet producer.

### `JetProducers/python`

- `AnomalousCellParameters_cfi.py`
  - Parameter block controlling allowed anomalous ECAL/HCAL cell counts.

- `CATopJetParameters_cfi.py`
  - Parameter block for CA top-jet tagging, including subjet pt fraction,
    adjacency, eta, and event-scale dependent cuts.

- `CMSBoostedTauSeedingParameters_cfi.py`
  - Parameter block for boosted tau seeding from subjets. It controls mass-drop,
    asymmetry, delta-R, and recursion depth cuts.

- `CaloJetParameters_cfi.py`
  - Standard CaloJet producer parameter block. It defines tower input, vertex
    correction, pileup offset, area/rho, thresholds, and jet type.

- `CaloTowerSchemeBWithHO_cfi.py`
  - CaloTower configuration clone enabling HO input.

- `CaloTowerSchemeB_cfi.py`
  - Standard CaloTower Scheme-B configuration clone with HO disabled.

- `CaloTowerSchemeBnoEE_cfi.py`
  - Explicit old CaloTower producer configuration without standard EE handling.
    It contains detailed ECAL/HCAL/HF/HO thresholds and anomalous-cell settings.

- `ECF_cff.py`
  - Sequence fragment defining multiple energy-correlation-function variants
    cloned from the generated `ECFAdder` cfi.

- `FastjetParameters_cfi.py`
  - Shared FastJet area/pileup parameter blocks for no-PU and with-PU modes.

- `GenJetParameters_cfi.py`
  - Standard GenJet producer parameter block. It sets generator particle input,
    jet type, thresholds, and area/rho options.

- `JetIDParams_cfi.py`
  - Shared CaloJet ID parameter block specifying rechit collections.

- `PFClusterJetParameters_cfi.py`
  - Standard PFClusterJet producer parameter block.

- `PFClustersForJets_cff.py`
  - Sequence building PFCluster reference candidates from ECAL, HCAL, HF, and HO
    clusters, then merging them for PFClusterJet input.

- `PFJetParameters_cfi.py`
  - Standard PFJet producer parameter block. It defines PF input, jet type,
    thresholds, FastJet area settings, and optional weights.

- `PileupJPTJetID_cfi.py`
  - Configuration for JPT pileup jet ID, including TMVA weight file paths.

- `PileupJetIDCutParams_cfi.py`
  - Working-point definitions for pileup jet ID across eras and eta/pt bins.

- `PileupJetIDParams_cfi.py`
  - Detailed MVA pileup jet ID training definitions: variables, eta bins,
    payloads, and algorithm versions.

- `PileupJetID_cfi.py`
  - Producer configurations for pileup jet ID modules and standard working
    points.

- `SubJetParameters_cfi.py`
  - Shared subjet producer parameter block.

- `TrackJetParameters_cfi.py`
  - Standard TrackJet parameter block. It defines track input, jet type, and
    thresholds.

- `TracksForJets_cff.py`
  - Track selection sequence for track jets. It prepares vertex-ref selected
    tracks.

- `ak4CaloJets_cfi.py`
  - AK4 CaloJet producer configuration using anti-kt R=0.4.

- `ak4GenJets_cfi.py`
  - AK4 GenJet producer configuration using anti-kt R=0.4.

- `ak4JetID_cfi.py`
  - AK4 CaloJet ID producer configuration.

- `ak4PFCaloJets_cfi.py`
  - Producer converting/constructing PF-style jets from calo-like inputs for
    compatibility studies.

- `ak4PFClusterJets_cfi.py`
  - AK4 PFClusterJet producer configuration.

- `ak4PFJetsBetaStar_cfi.py`
  - Configuration for beta-star-related PFJet pileup variables.

- `ak4PFJets_cfi.py`
  - AK4 PFJet producer configuration using anti-kt R=0.4. This is the standard
    small-R PF jet definition.

- `ak4TrackJets_cfi.py`
  - AK4 TrackJet producer configuration.

- `ak5CastorJetID_cfi.py`
  - AK5 CASTOR jet ID configuration.

- `ak5CastorJets_cfi.py`
  - AK5 CASTOR jet producer configuration.

- `ak7CastorJetID_cfi.py`
  - AK7 CASTOR jet ID configuration.

- `ak7CastorJets_cfi.py`
  - AK7 CASTOR jet producer configuration.

- `ak8GenJets_cfi.py`
  - AK8 GenJet producer configuration for large-R truth jets.

- `ak8PFJetsCHS_groomingValueMaps_cfi.py`
  - Value-map configuration for AK8 CHS grooming observables.

- `ak8PFJetsPuppi_groomingValueMaps_cfi.py`
  - Value-map configuration for AK8 Puppi grooming observables.

- `ak8PFJets_cfi.py`
  - Main AK8 PFJet configuration. It defines ungroomed, CHS, Puppi,
    constituent-subtraction, constituent selectors, and filtered/pruned/softdrop
    /trimmed large-R variants.

- `ca15PFJets_cfi.py`
  - CA15 PFJet configuration for very large-R boosted-object studies.

- `caSubjetFilterGenJets_cfi.py`
  - Cambridge-Aachen subjet-filter configuration for GenJets.

- `caSubjetFilterPFJets_cfi.py`
  - Cambridge-Aachen subjet-filter configuration for PFJets.

- `caTopTaggers_cff.py`
  - CA top-tagging sequence fragment. It defines CMS, HEP, and JHU-style top-tag
    PF jets and associated tag-info producers.

- `caloJetsForTrk_cff.py`
  - CaloJet sequence fragment used as input to track/JPT-related workflows.

- `fixedGridRhoProducerFastjet_cfi.py`
  - FastJet fixed-grid rho producer configurations for all, central, charged,
    neutral, calo, and related variants.

- `fixedGridRhoProducer_cfi.py`
  - Standard fixed-grid rho producer configurations.

- `hepTopTaggerV2_cff.py`
  - HEPTopTagger v2 sequence/configuration fragment.

- `hltMVAJetPuId_cff.py`
  - HLT-oriented MVA pileup jet ID configuration.

- `hltPUIdAlgo_cff.py`
  - HLT pileup-ID algorithm configuration and working points.

- `hltParticleFlowForJets_cfi.py`
  - HLT-like particle-flow reconstruction fragment specialized for jet inputs.

- `hltak4CaloJets_cfi.py`
  - HLT AK4 CaloJet producer configuration.

- `kt4PFJets_cfi.py`
  - kt R=0.4 PFJet producer configuration. Often used for rho estimation.

- `kt6PFJets_cfi.py`
  - kt R=0.6 PFJet producer configuration. Often used historically for rho
    estimation.

- `nJettinessAdder_cfi.py`
  - Configuration for N-subjettiness value-map production, defaulting to AK8
    Puppi jets.

- `pileupjetidproducer_cfi.py`
  - Additional pileup jet ID producer configuration fragment.

- `qjetsadder_cfi.py`
  - Configuration for Q-jets value-map production, defaulting to AK8 CHS jets.

### `JetProducers/src`

- `AnomalousTower.cc`
  - Implementation of anomalous calorimeter tower helper logic.

- `BackgroundEstimator.cc`
  - Implementation of background estimation utilities.

- `CastorJetIDHelper.cc`
  - Implementation of CASTOR jet ID helper calculations.

- `JetIDHelper.cc`
  - Implementation of CaloJet ID helper calculations from towers/rechits.

- `JetMatchingTools.cc`
  - Implementation of reusable jet matching utilities.

- `JetMuonHitsIDHelper.cc`
  - Implementation of muon-hit-related jet ID helper logic.

- `JetSpecific.cc`
  - Implementation of type-specific jet filling utilities.

- `MVAJetPuId.cc`
  - Implementation of MVA pileup jet ID variable calculation and discriminator
    logic.

- `PileUpSubtractor.cc`
  - Implementation of pileup/underlying-event subtraction helper logic.

- `PileupJPTJetIdAlgo.cc`
  - Implementation of JPT pileup jet ID algorithm.

- `PileupJetIdAlgo.cc`
  - Implementation of standard pileup jet ID algorithm and variables.

### `JetProducers/test`

- `HTTV2_test.py`
  - Test configuration for HEPTopTagger v2.

- `PFClusterJets_PFCaloJets_producer.py`
  - Test job producing PFClusterJets and PFCaloJets for comparison.

- `analyzeJets.C`
  - ROOT macro for analyzing produced jet collections.

- `analyzeJetsChain.C`
  - ROOT macro variant for chained input files.

- `analyzeJets_head.C`
  - Header/helper macro for `analyzeJets.C`.

- `analyzeJets_headChain.C`
  - Header/helper macro for chained jet analysis.

- `fixedGridTest_cfg.py`
  - Test configuration for fixed-grid rho producers.

- `prepareCompile.C`
  - ROOT macro helper for compiling analysis macros.

- `runJetReco_Substructure_cfg.py`
  - Test job for jet reconstruction with substructure modules.

- `runJetReco_cfg.py`
  - Basic test job for standard jet reconstruction.

- `runPileupModules_cfg.py`
  - Test job for pileup-related jet modules.

- `testJetTools_cfg.py`
  - Test configuration for jet tools and substructure add-ons.

- `testJetTools_onMiniAOD_cfg.py`
  - MiniAOD-oriented test configuration for jet tools.

### `JetProducers/validation`

- `README`
  - Validation instructions for comparing FastjetJetProducer output against
    reference jet producer output.

- `fastjetJetProducer_validation_cfg.py`
  - Validation job for FastJet producer outputs.

- `jetProducers_validation_cfg.py`
  - Reference validation job for standard jet producers.

- `validation.sh`
  - Shell script driving comparison/plot production from validation ROOT files.

