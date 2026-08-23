# RecoMET Package Overview

RecoMET is the CMSSW reconstruction package for missing transverse momentum
(MET, or missing transverse energy in older naming) and closely related event
quality quantities.  From a physics point of view, the package answers three
questions:

1. What visible transverse momentum was reconstructed in the event?
2. Which detector or reconstruction pathologies can fake large MET?
3. How should pileup and object resolutions be accounted for when interpreting
   the MET vector?

## Recommended Learning Order

Start with **METProducers**.  This subpackage shows the physics objects that are
actually written into the event: calorimeter MET, PF MET, charged PF MET,
generator-level MET, MET significance, HCAL noise information, and beam-halo
summary objects.

Then read **METAlgorithms**.  These are the lower-level calculations used by the
producers.  This is where the MET vector, detector-specific information,
significance matrices, muon corrections, HCAL noise, and halo-identification
logic are implemented.

Next read **Configuration**.  These files connect producers and algorithms into
standard CMSSW reconstruction sequences and event-content definitions.  They are
the best place to see which modules run together in normal workflows.

After that read **METFilters**.  These filters are not MET producers, but they
are essential for physics use of MET because they reject or tag events with
known fake-MET sources: bad muons, dead ECAL cells, HCAL laser/noise problems,
beam halo, tracking failures, and bad vertices.

Finally read **METPUSubtraction**.  This is the advanced pileup-mitigation area:
MVA MET, no-pileup MET, JVF-based jet classification, and DeepMET/Triton
inference.  It is technically richer and easier to understand after the basic
MET producer and algorithm flow is clear.

## Subpackage Map

```text
RecoMET/
|-- Configuration/       Standard reconstruction sequences and event content.
|-- METAlgorithms/       C++ algorithm library for MET, significance, noise, and halo.
|-- METProducers/        CMSSW EDProducers that create MET and related products.
|-- METFilters/          CMSSW EDFilters for fake-MET and event-quality rejection.
`-- METPUSubtraction/    Pileup-mitigated MET, MVA MET, no-PU MET, and DeepMET.
```

Generated `__pycache__` files are intentionally omitted from this overview.

## Configuration

**Role:** high-level CMSSW python fragments that assemble RecoMET modules into
standard reconstruction sequences.

```text
Configuration/
`-- python/
    |-- GenMETParticles_cff.py
    |-- RecoGenMET_cff.py
    |-- RecoMET_BeamHaloId_cff.py
    |-- RecoMET_Cosmics_cff.py
    |-- RecoMET_EventContent_cff.py
    |-- RecoMET_cff.py
    |-- RecoPFMET_cff.py
    `-- RecoTCMET_cff.py
```

- `python/GenMETParticles_cff.py`  
  Defines generator-particle collections used for generator-level MET.  It
  removes invisible particles such as neutrinos when building visible gen-MET
  inputs.

- `python/RecoGenMET_cff.py`  
  Builds the standard generator-level MET task and sequence.  It connects true
  gen MET and calorimeter-style gen MET configurations.

- `python/RecoMET_BeamHaloId_cff.py`  
  Assembles CSC, ECAL, HCAL, global halo, and summary producers into the beam
  halo identification sequence.  This is the configuration-level entry point
  for halo-related fake-MET diagnostics.

- `python/RecoMET_Cosmics_cff.py`  
  Defines MET reconstruction sequences specialized for cosmic workflows.  It
  provides variants with or without beam-halo and HCAL-noise components.

- `python/RecoMET_EventContent_cff.py`  
  Lists RecoMET products kept in AOD, RECO, and FEVT event content.  Use this
  when debugging why a MET, halo, or HCAL-noise product is present or absent in
  an output tier.

- `python/RecoMET_cff.py`  
  Main calorimeter-oriented MET reconstruction sequence.  It includes calo MET,
  muon corrections, HCAL noise information, and beam-halo identification, with
  era-dependent handling for Phase-2 HCAL.

- `python/RecoPFMET_cff.py`  
  Main PF MET sequence.  It configures PF MET, charged PF MET, PUPPI without
  leptons, and PUPPI MET; heavy-ion process modifiers remove unsupported pieces.

- `python/RecoTCMET_cff.py`  
  Tracker-corrected MET sequence.  This is a compact entry point for legacy
  track-corrected MET studies.

## METAlgorithms

**Role:** reusable C++ algorithm code.  Producers call these classes to compute
MET vectors, detector-specific payloads, significance, HCAL noise quantities,
and beam-halo quantities.

```text
METAlgorithms/
|-- BuildFile.xml
|-- interface/
|   |-- CSCHaloAlgo.h
|   |-- CaloSpecificAlgo.h
|   |-- EcalHaloAlgo.h
|   |-- GenSpecificAlgo.h
|   |-- GlobalHaloAlgo.h
|   |-- HcalHPDRBXMap.h
|   |-- HcalHaloAlgo.h
|   |-- HcalNoiseAlgo.h
|   |-- HcalNoiseRBXArray.h
|   |-- METAlgo.h
|   |-- METSignificance.h
|   |-- MuonMETAlgo.h
|   |-- MuonMETInfo.h
|   |-- PFClusterSpecificAlgo.h
|   |-- PFSpecificAlgo.h
|   |-- SignAlgoResolutions.h
|   |-- SignCaloSpecificAlgo.h
|   |-- SignPFSpecificAlgo.h
|   |-- TCMETAlgo.h
|   `-- significanceAlgo.h
`-- src/
    |-- CSCHaloAlgo.cc
    |-- CaloSpecificAlgo.cc
    |-- EcalHaloAlgo.cc
    |-- GenSpecificAlgo.cc
    |-- GlobalHaloAlgo.cc
    |-- HcalHPDRBXMap.cc
    |-- HcalHaloAlgo.cc
    |-- HcalNoiseAlgo.cc
    |-- HcalNoiseRBXArray.cc
    |-- METAlgo.cc
    |-- METSignificance.cc
    |-- MuonMETAlgo.cc
    |-- PFClusterSpecificAlgo.cc
    |-- PFSpecificAlgo.cc
    |-- SignAlgoResolutions.cc
    |-- SignCaloSpecificAlgo.cc
    |-- SignPFSpecificAlgo.cc
    |-- TCMETAlgo.cc
    `-- significanceAlgo.cc
```

- `BuildFile.xml`  
  Declares CMSSW build dependencies for the algorithm library.  Check this when
  adding new data formats, geometry, conditions, or math dependencies.

- `interface/METAlgo.h` / `src/METAlgo.cc`  
  Base MET algorithm for summing input candidates into a MET vector.  This is
  the simplest place to understand the sign convention: MET is the negative
  visible transverse momentum sum.

- `interface/CaloSpecificAlgo.h` / `src/CaloSpecificAlgo.cc`  
  Computes calorimeter-specific MET information from calorimeter towers.  It
  fills detector-region and energy-fraction details that accompany CaloMET.

- `interface/PFSpecificAlgo.h` / `src/PFSpecificAlgo.cc`  
  Computes PF-specific MET payloads from particle-flow candidates.  It separates
  contributions by PF candidate type, which is useful for diagnosing which
  reconstructed particle category drives MET.

- `interface/PFClusterSpecificAlgo.h` / `src/PFClusterSpecificAlgo.cc`  
  Computes MET using PF clusters rather than full PF candidates.  This supports
  PF-cluster MET, a calorimeter-cluster-based missing momentum observable.

- `interface/GenSpecificAlgo.h` / `src/GenSpecificAlgo.cc`  
  Computes generator-level MET-specific information from gen particles.  It is
  the algorithmic counterpart of the gen-MET producer configurations.

- `interface/TCMETAlgo.h` / `src/TCMETAlgo.cc`  
  Implements tracker-corrected MET, using tracks to correct calorimeter response
  and muon-related effects.  This is legacy but useful for learning how track
  information can modify a raw calorimeter MET vector.

- `interface/MuonMETAlgo.h` / `src/MuonMETAlgo.cc`  
  Calculates muon corrections for MET, including calorimeter-energy handling
  associated with reconstructed muons.  This underlies the muon value maps used
  to correct CaloMET and TCMET.

- `interface/MuonMETInfo.h`  
  Small data structure carrying per-muon information relevant for MET
  corrections.  It is used by muon-correction algorithms and value-map
  producers.

- `interface/METSignificance.h` / `src/METSignificance.cc`  
  High-level MET significance calculation.  It combines object resolutions into
  a covariance matrix and evaluates how unlikely the observed MET is under
  detector resolution effects.

- `interface/significanceAlgo.h` / `src/significanceAlgo.cc`  
  Legacy significance algorithm using matrix operations.  It supports older
  tower/object-based significance calculations.

- `interface/SignAlgoResolutions.h` / `src/SignAlgoResolutions.cc`  
  Resolution parameter handling for MET significance.  It maps object types to
  resolution functions and parameters used in covariance construction.

- `interface/SignCaloSpecificAlgo.h` / `src/SignCaloSpecificAlgo.cc`  
  Calorimeter-object contribution to MET significance.  It translates calo
  energy deposits into resolution terms.

- `interface/SignPFSpecificAlgo.h` / `src/SignPFSpecificAlgo.cc`  
  PF-object contribution to MET significance.  It provides PF-candidate
  resolution modeling for the significance matrix.

- `interface/HcalNoiseAlgo.h` / `src/HcalNoiseAlgo.cc`  
  Implements HCAL noise identification logic from rechits, towers, and RBX/HPD
  information.  This is central for rejecting fake MET from HCAL electronics or
  pulse-shape pathologies.

- `interface/HcalNoiseRBXArray.h` / `src/HcalNoiseRBXArray.cc`  
  Container organizing HCAL noise information by RBX.  It makes it easier for
  the noise algorithm to aggregate channel-level information into detector
  hardware units.

- `interface/HcalHPDRBXMap.h` / `src/HcalHPDRBXMap.cc`  
  Mapping between HCAL HPD/RBX hardware identifiers and detector channels.  This
  supports RBX-level noise classification.

- `interface/CSCHaloAlgo.h` / `src/CSCHaloAlgo.cc`  
  Finds beam-halo signatures using CSC information and related event-level
  quantities.  CSC halo is an important non-collision source of apparent MET.

- `interface/EcalHaloAlgo.h` / `src/EcalHaloAlgo.cc`  
  Computes ECAL-based halo observables.  These quantities complement CSC and
  HCAL halo information when identifying beam-halo events.

- `interface/HcalHaloAlgo.h` / `src/HcalHaloAlgo.cc`  
  Computes HCAL-based halo observables.  This helps identify beam-halo energy
  deposits that can bias calorimeter MET.

- `interface/GlobalHaloAlgo.h` / `src/GlobalHaloAlgo.cc`  
  Combines detector-specific halo information into global halo decisions and
  summary quantities.  It bridges subsystem observables to event-level halo
  classification.

## METProducers

**Role:** CMSSW EDProducers that read event data, call algorithms, and write MET
or MET-related event products.

```text
METProducers/
|-- BuildFile.xml
|-- interface/
|   |-- BeamHaloSummaryProducer.h
|   |-- CSCHaloDataProducer.h
|   |-- CaloMETProducer.h
|   |-- EcalHaloDataProducer.h
|   |-- ElseMETProducer.h
|   |-- GenMETProducer.h
|   |-- GlobalHaloDataProducer.h
|   |-- HcalHaloDataProducer.h
|   |-- HcalNoiseInfoProducer.h
|   |-- METSignificanceProducer.h
|   |-- MinMETProducerT.h
|   |-- MuonMET.h
|   |-- MuonMETValueMapProducer.h
|   |-- MuonTCMETValueMapProducer.h
|   |-- PFClusterMETProducer.h
|   |-- PFMETProducer.h
|   |-- ParticleFlowForChargedMETProducer.h
|   `-- TCMETProducer.h
|-- python/
|   |-- BeamHaloSummary_cfi.py
|   |-- CSCHaloData_cfi.py
|   |-- CaloMET_cfi.py
|   |-- EcalHaloData_cfi.py
|   |-- GlobalHaloData_cfi.py
|   |-- HcalHaloData_cfi.py
|   |-- METSigParams_cfi.py
|   |-- METSignificanceObjects_cfi.py
|   |-- METSignificanceParams_cfi.py
|   |-- METSignificance_cfi.py
|   |-- MetMuonCorrections_cff.py
|   |-- MuonMETValueMapProducer_cff.py
|   |-- MuonTCMETValueMapProducer_cff.py
|   |-- PFClusterMET_cfi.py
|   |-- TCMET_cfi.py
|   |-- caloMetM_cfi.py
|   |-- genMetCaloAndNonPrompt_cfi.py
|   |-- genMetCalo_cfi.py
|   |-- genMetFromGenJets_cfi.py
|   |-- genMetTrue_cfi.py
|   |-- hcalnoiseinfoproducer_cfi.py
|   |-- pfChMet_cfi.py
|   `-- testInputFiles_cff.py
|-- src/
|   |-- BeamHaloSummaryProducer.cc
|   |-- CSCHaloDataProducer.cc
|   |-- CaloMETProducer.cc
|   |-- CaloRecHitsBeamHaloCleaned.cc
|   |-- EcalHaloDataProducer.cc
|   |-- ElseMETProducer.cc
|   |-- GenMETProducer.cc
|   |-- GlobalHaloDataProducer.cc
|   |-- HcalHaloDataProducer.cc
|   |-- HcalNoiseInfoProducer.cc
|   |-- METSignificanceProducer.cc
|   |-- MinMETProducerT.cc
|   |-- MuonMET.cc
|   |-- MuonMETValueMapProducer.cc
|   |-- MuonTCMETValueMapProducer.cc
|   |-- PFClusterMETProducer.cc
|   |-- PFMETProducer.cc
|   |-- ParticleFlowForChargedMETProducer.cc
|   |-- PoolFileCatalog.xml
|   |-- SealModule.cc
|   `-- TCMETProducer.cc
`-- test/
    |-- BuildFile.xml
    |-- recoMET_METSignificance_cfg.py
    |-- recoMET_caloMet_cfg.py
    |-- recoMET_genMet_cfg.py
    |-- recoMET_pfChMet_cfg.py
    |-- recoMET_pfClusterMet_cfg.py
    |-- recoMET_pfMet_cfg.py
    |-- recoMET_tcMet_cfg.py
    `-- runtests.sh
```

- `BuildFile.xml`  
  Build dependencies for producer plugins and libraries.  It records which
  CMSSW data formats, geometry, framework, and algorithm libraries the producer
  package needs.

- `interface/CaloMETProducer.h` / `src/CaloMETProducer.cc`  
  Producer for calorimeter MET from calo towers.  It wraps `CaloSpecificAlgo`
  and writes reconstructed CaloMET collections.

- `interface/PFMETProducer.h` / `src/PFMETProducer.cc`  
  Producer for particle-flow MET from PF candidates.  This is the central
  physics producer for standard reconstructed MET in modern CMS workflows.

- `interface/PFClusterMETProducer.h` / `src/PFClusterMETProducer.cc`  
  Producer for PF-cluster MET.  It uses calorimeter-like PF cluster inputs and
  is useful for studying calorimeter response with PF reconstruction inputs.

- `interface/ParticleFlowForChargedMETProducer.h` / `src/ParticleFlowForChargedMETProducer.cc`  
  Selects charged PF candidates for charged MET production.  This supports
  charged-hadron-based MET observables and pileup studies.

- `interface/TCMETProducer.h` / `src/TCMETProducer.cc`  
  Producer for tracker-corrected MET.  It applies track and muon information to
  correct calorimeter MET response.

- `interface/GenMETProducer.h` / `src/GenMETProducer.cc`  
  Producer for generator-level MET.  It is used to make truth-level MET products
  for simulation validation and performance studies.

- `interface/ElseMETProducer.h` / `src/ElseMETProducer.cc`  
  Generic/minimal MET producer variant for specialized input collections.  It is
  part of the older MET producer infrastructure.

- `interface/MinMETProducerT.h` / `src/MinMETProducerT.cc`  
  Template base/helper for MET producer implementations.  It factors common
  producer behavior used by specific MET collection types.

- `interface/METSignificanceProducer.h` / `src/METSignificanceProducer.cc`  
  Produces MET significance quantities from reconstructed objects and resolution
  parameters.  This product helps distinguish genuine invisible momentum from
  detector-resolution fluctuations.

- `interface/MuonMET.h` / `src/MuonMET.cc`  
  Legacy muon correction module for MET.  It writes correction information for
  how reconstructed muons affect the MET vector.

- `interface/MuonMETValueMapProducer.h` / `src/MuonMETValueMapProducer.cc`  
  Produces value maps containing per-muon MET correction information.  These
  maps are used by calorimeter MET correction configurations.

- `interface/MuonTCMETValueMapProducer.h` / `src/MuonTCMETValueMapProducer.cc`  
  Produces per-muon value maps specialized for tracker-corrected MET.  It
  complements the standard muon MET value-map producer.

- `interface/HcalNoiseInfoProducer.h` / `src/HcalNoiseInfoProducer.cc`  
  Produces HCAL noise summary information from rechits and towers.  This product
  is later consumed by filters or event-content definitions to diagnose fake MET.

- `interface/CSCHaloDataProducer.h` / `src/CSCHaloDataProducer.cc`  
  Produces CSC-based halo data.  It wraps `CSCHaloAlgo` and writes the CSC halo
  observables used in beam-halo identification.

- `interface/EcalHaloDataProducer.h` / `src/EcalHaloDataProducer.cc`  
  Produces ECAL-based halo data.  It records ECAL observables relevant for
  non-collision beam-halo backgrounds.

- `interface/HcalHaloDataProducer.h` / `src/HcalHaloDataProducer.cc`  
  Produces HCAL-based halo data.  It records HCAL observables that can identify
  halo-like energy deposits.

- `interface/GlobalHaloDataProducer.h` / `src/GlobalHaloDataProducer.cc`  
  Produces global halo data by combining subsystem halo inputs.  This is the
  bridge between detector-level halo observables and event-level halo decisions.

- `interface/BeamHaloSummaryProducer.h` / `src/BeamHaloSummaryProducer.cc`  
  Produces the final beam-halo summary object.  It packages loose/tight halo
  decisions for downstream filters and event interpretation.

- `src/CaloRecHitsBeamHaloCleaned.cc`  
  Utility implementation for cleaning calorimeter rechits affected by beam-halo
  signatures.  It is part of the halo-cleaning support code rather than a normal
  standalone MET producer.

- `src/SealModule.cc`  
  Registers several producer plugins with the CMSSW framework.  If a producer
  exists but cannot be loaded, this is one of the files to inspect.

- `src/PoolFileCatalog.xml`  
  Local XML catalog used by tests or legacy workflows.  It is not physics logic,
  but it can affect file resolution in local runs.

- `python/CaloMET_cfi.py`  
  Python configuration for the standard CaloMET producer.  It defines input tags
  and producer parameters used by the main calorimeter MET sequence.

- `python/caloMetM_cfi.py`  
  Configures muon-corrected calorimeter MET.  It combines calo MET with muon
  correction value maps.

- `python/PFClusterMET_cfi.py`  
  Configures PF-cluster MET production.  Use this to find the default PF cluster
  inputs and producer parameters.

- `python/pfChMet_cfi.py`  
  Configures charged PF MET.  It uses the charged PF candidate selector and then
  builds a charged-only MET observable.

- `python/TCMET_cfi.py`  
  Configures tracker-corrected MET.  It exposes the input collections and
  correction settings used by `TCMETProducer`.

- `python/genMetTrue_cfi.py`  
  Configures true generator-level MET.  This is the main truth MET reference in
  simulation.

- `python/genMetCalo_cfi.py`  
  Configures calorimeter-style generator MET.  It is useful for comparing
  reconstructed calorimeter MET against a truth-level visible-particle analog.

- `python/genMetCaloAndNonPrompt_cfi.py`  
  Configures a gen-MET variant including non-prompt components.  This supports
  specialized simulation comparisons.

- `python/genMetFromGenJets_cfi.py`  
  Configures MET built from generator jets.  It provides a jet-level truth
  comparison rather than a particle-level one.

- `python/hcalnoiseinfoproducer_cfi.py`  
  Configures the HCAL noise information producer.  Use this to inspect default
  HCAL noise inputs and thresholds.

- `python/BeamHaloSummary_cfi.py`  
  Configures the final beam-halo summary producer.  This is the python fragment
  that packages subsystem halo results into the summary product.

- `python/CSCHaloData_cfi.py`  
  Configures CSC halo data production.  It supplies the CSC-based input to the
  beam-halo identification sequence.

- `python/EcalHaloData_cfi.py`  
  Configures ECAL halo data production.  It supplies ECAL observables used in
  halo diagnostics.

- `python/HcalHaloData_cfi.py`  
  Configures HCAL halo data production.  It supplies HCAL observables used in
  halo diagnostics.

- `python/GlobalHaloData_cfi.py`  
  Configures global halo data production.  It combines subsystem halo quantities
  into a global halo data product.

- `python/MuonMETValueMapProducer_cff.py`  
  Configures standard muon MET correction value maps.  These maps are consumed
  by calorimeter MET correction workflows.

- `python/MuonTCMETValueMapProducer_cff.py`  
  Configures tracker-corrected MET muon value maps.  These maps are specialized
  for TCMET correction workflows.

- `python/MetMuonCorrections_cff.py`  
  Collects muon correction modules into a sequence.  It is the python-level
  entry point for applying muon-related MET corrections.

- `python/METSignificance_cfi.py`  
  Configures the MET significance producer.  It connects reconstructed inputs to
  the significance algorithm.

- `python/METSignificanceObjects_cfi.py`  
  Defines object collections used by MET significance.  This is useful when
  debugging which reconstructed objects contribute to the covariance matrix.

- `python/METSignificanceParams_cfi.py`  
  Stores the main MET significance parameter set.  These parameters control how
  reconstructed object resolutions enter the significance covariance.

- `python/METSigParams_cfi.py`  
  Stores legacy or alternate MET significance parameters.  It is useful when
  comparing older significance configurations against current ones.

- `python/testInputFiles_cff.py`  
  Shared input-file definitions for producer tests.  It keeps the test
  configurations compact.

- `test/recoMET_pfMet_cfg.py`  
  Test cmsRun configuration for PF MET production.  It is the most direct test
  example for the standard reconstructed MET product.

- `test/recoMET_caloMet_cfg.py`  
  Test cmsRun configuration for CaloMET production.  Use it to see a minimal
  calorimeter MET workflow.

- `test/recoMET_tcMet_cfg.py`  
  Test cmsRun configuration for tracker-corrected MET.  It exercises the legacy
  TCMET producer path.

- `test/recoMET_genMet_cfg.py`  
  Test cmsRun configuration for generator-level MET.  It is useful for checking
  truth-MET production in simulation.

- `test/recoMET_pfChMet_cfg.py`  
  Test cmsRun configuration for charged PF MET.  It exercises the charged PF
  candidate selection and charged MET producer path.

- `test/recoMET_pfClusterMet_cfg.py`  
  Test cmsRun configuration for PF-cluster MET.  It validates cluster-based MET
  reconstruction.

- `test/recoMET_METSignificance_cfg.py`  
  Test cmsRun configuration for MET significance.  It is the best producer test
  for checking significance inputs and resolution parameters.

- `test/runtests.sh`  
  Shell runner for producer tests.  It calls the individual cmsRun test
  configurations and reports failures.

- `test/BuildFile.xml`  
  Build metadata for the producer test area.  It declares test-time dependencies
  used by the cmsRun configurations.

## METFilters

**Role:** filters for event pathologies that can produce fake MET or invalidate
MET interpretation.

```text
METFilters/
|-- data/
|   `-- hcalLaserBadEvents_2011.py
|-- interface/
|   `-- EcalBoundaryInfoCalculator.h
|-- plugins/
|   |-- BadGlobalMuonTagger.cc
|   |-- BadParticleFilter.cc
|   |-- BuildFile.xml
|   |-- CSCTightHalo2015Filter.cc
|   |-- CSCTightHaloFilter.cc
|   |-- CSCTightHaloTrkMuUnvetoFilter.cc
|   |-- ChargedHadronTrackResolutionFilter.cc
|   |-- EEBadScFilter.cc
|   |-- EENoiseFilter.cc
|   |-- EcalBadCalibFilter.cc
|   |-- EcalDeadCellBoundaryEnergyFilter.cc
|   |-- EcalDeadCellDeltaRFilter.cc
|   |-- EcalDeadCellTriggerPrimitiveFilter.cc
|   |-- EcalLaserCorrFilter.cc
|   |-- GlobalSuperTightHalo2016Filter.cc
|   |-- GlobalTightHalo2016Filter.cc
|   |-- GreedyMuonPFCandidateFilter.cc
|   |-- HFNoisyHitsFilter.cc
|   |-- HcalLaserEventFilter.cc
|   |-- HcalStripHaloFilter.cc
|   |-- InconsistentMuonPFCandidateFilter.cc
|   |-- JetIDFailureFilter.cc
|   |-- MultiEventFilter.cc
|   |-- MuonBadTrackFilter.cc
|   `-- TrackingFailureFilter.cc
|-- python/
|   |-- BadChargedCandidateFilter_cfi.py
|   |-- BadChargedCandidateSummer16Filter_cfi.py
|   |-- BadPFMuonDzFilter_cfi.py
|   |-- BadPFMuonSummer16Filter_cfi.py
|   |-- CSCTightHalo2015Filter_cfi.py
|   |-- CSCTightHaloFilter_cfi.py
|   |-- CSCTightHaloTrkMuUnvetoFilter_cfi.py
|   |-- EcalDeadCellBoundaryEnergyFilter_cfi.py
|   |-- EcalDeadCellTriggerPrimitiveFilter_cfi.py
|   |-- GenerateHcalLaserBadRunList.py
|   |-- HcalStripHaloFilter_cfi.py
|   |-- badGlobalMuonTaggerFWLite.py
|   |-- badGlobalMuonTaggersAOD_cff.py
|   |-- badGlobalMuonTaggersMiniAOD_cff.py
|   |-- chargedHadronTrackResolutionFilter_cfi.py
|   |-- ecalBadCalibFilter_cfi.py
|   |-- ecalLaserCorrFilter_cfi.py
|   |-- eeBadScFilter_cfi.py
|   |-- eeNoiseFilter_cfi.py
|   |-- globalSuperTightHalo2016Filter_cfi.py
|   |-- globalTightHalo2016Filter_cfi.py
|   |-- greedyMuonPFCandidateFilter_cfi.py
|   |-- hcalLaserBadEvents_2011.py
|   |-- hcalLaserEventFilter_cfi.py
|   |-- inconsistentMuonPFCandidateFilter_cfi.py
|   |-- jetIDFailureFilter_cfi.py
|   |-- metFilters_cff.py
|   |-- multiEventFilter_cfi.py
|   |-- muonBadTrackFilter_cfi.py
|   |-- primaryVertexFilter_cfi.py
|   |-- scrapingFilter_cfi.py
|   |-- trackingFailureFilter_cfi.py
|   |-- trackingPOGFilters_cff.py
|   `-- trackingPOGFilters_cfi.py
`-- test/
    |-- exampleICHEPrecommendation_cfg.py
    |-- exampleRecommendation_cfg.py
    |-- filters_cfg.py
    |-- test_badChargedCandidateFilter.py
    `-- test_badMuonCandidateFilter.py
```

- `data/hcalLaserBadEvents_2011.py`  
  Static list of known HCAL laser bad events from 2011.  It supports legacy
  HCAL laser filtering.

- `interface/EcalBoundaryInfoCalculator.h`  
  Helper for ECAL dead-cell boundary calculations.  It is used by filters that
  quantify energy around masked or dead ECAL regions.

- `plugins/BadParticleFilter.cc`  
  Implements bad PF muon and bad charged candidate filters, including Summer16
  variants and a dz-based muon variant.  These reject events where badly
  reconstructed muons or charged candidates can create fake MET.

- `plugins/BadGlobalMuonTagger.cc`  
  Tags bad global muons and clone-like global muons.  It supports AOD/MiniAOD
  bad-muon cleaning workflows.

- `plugins/ChargedHadronTrackResolutionFilter.cc`  
  Rejects events with charged hadron PF candidates matched to tracks with poor
  momentum resolution.  Such tracks can create large fake MET through
  mismeasured charged particles.

- `plugins/GreedyMuonPFCandidateFilter.cc`  
  Filters events where PF candidates are greedily or incorrectly associated with
  muons.  This targets fake MET from muon/PF reconstruction inconsistencies.

- `plugins/InconsistentMuonPFCandidateFilter.cc`  
  Filters inconsistent PF muon candidates.  It protects MET from cases where PF
  candidate kinematics and muon reconstruction disagree.

- `plugins/MuonBadTrackFilter.cc`  
  Filters events containing muons with problematic tracks.  It is another
  muon-driven fake-MET protection module.

- `plugins/CSCTightHaloFilter.cc`  
  CSC tight beam-halo filter.  It targets non-collision muon activity aligned
  with the beam direction.

- `plugins/CSCTightHalo2015Filter.cc`  
  2015-era CSC tight halo filter definition.  It preserves the historical
  recommendation used for that data-taking period.

- `plugins/CSCTightHaloTrkMuUnvetoFilter.cc`  
  CSC tight halo filter variant without the tracker-muon veto.  It is useful
  when studying halo decisions before applying that veto.

- `plugins/GlobalTightHalo2016Filter.cc`  
  Event-level 2016 global tight halo filter.  It uses global halo summary
  decisions to reject halo-induced fake MET.

- `plugins/GlobalSuperTightHalo2016Filter.cc`  
  Stricter 2016 global halo filter.  It applies the super-tight halo decision
  for analyses that need stronger halo rejection.

- `plugins/HcalStripHaloFilter.cc`  
  HCAL strip-based halo filter.  It identifies halo-like deposits in HCAL that
  can bias calorimeter and PF MET.

- `plugins/HcalLaserEventFilter.cc`  
  Rejects or tags known HCAL laser events.  It is driven by configured bad-event
  lists and era-dependent behavior.

- `plugins/HFNoisyHitsFilter.cc`  
  Filters noisy HF hit patterns.  HF noise can create forward energy imbalance
  and therefore fake MET.

- `plugins/EcalDeadCellTriggerPrimitiveFilter.cc`  
  Identifies events where dead ECAL trigger primitives can hide visible energy.
  Missing ECAL energy near dead regions is a direct fake-MET risk.

- `plugins/EcalDeadCellBoundaryEnergyFilter.cc`  
  ECAL dead-cell filter based on boundary energy around masked/dead regions.  It
  diagnoses missing ECAL response that may bias MET.

- `plugins/EcalDeadCellDeltaRFilter.cc`  
  ECAL dead-cell filter based on angular proximity to problematic regions.  It
  catches objects close enough to dead cells to create fake MET risk.

- `plugins/EcalBadCalibFilter.cc`  
  Filters events affected by problematic ECAL channels with bad calibration.
  This is a standard fake-MET cleanup for known bad ECAL cells.

- `plugins/EcalLaserCorrFilter.cc`  
  Filters events using ECAL laser correction information.  It targets ECAL
  response problems that can produce anomalous MET.

- `plugins/EEBadScFilter.cc`  
  Endcap ECAL bad-supercluster filter.  It removes events with known problematic
  EE supercluster signatures.

- `plugins/EENoiseFilter.cc`  
  Endcap ECAL noise filter.  It targets EE noise patterns that can create
  anomalous energy imbalance.

- `plugins/JetIDFailureFilter.cc`  
  Filters events failing jet ID criteria.  Bad jets can dominate the visible
  momentum sum and create fake MET.

- `plugins/TrackingFailureFilter.cc`  
  Filters events with tracking failures that can corrupt PF reconstruction.
  Since PF MET depends strongly on tracks, tracking failures are a major MET
  quality issue.

- `plugins/MultiEventFilter.cc`  
  Utility filter for selecting or vetoing configured events.  It is useful for
  testing and event-list-based workflows.

- `plugins/BuildFile.xml`  
  Build dependencies and plugin declarations for MET filters.

- `python/BadPFMuonSummer16Filter_cfi.py`  
  Configures the Summer16 bad PF muon filter.  It sets the `BadParticleFilter`
  mode and thresholds for that recommendation.

- `python/BadPFMuonDzFilter_cfi.py`  
  Configures the dz-based bad PF muon filter.  It adds a longitudinal impact
  parameter criterion to the bad-muon cleaning logic.

- `python/BadChargedCandidateFilter_cfi.py`  
  Configures the bad charged candidate filter.  It targets charged PF candidates
  matched to problematic muon tracks.

- `python/BadChargedCandidateSummer16Filter_cfi.py`  
  Configures the Summer16 bad charged candidate filter.  It preserves the
  thresholds and mode used in the Summer16 cleaning recommendation.

- `python/badGlobalMuonTaggersAOD_cff.py`  
  AOD bad global muon tagging sequence.  It configures clone and bad-global-muon
  taggers for full reconstructed muon collections.

- `python/badGlobalMuonTaggersMiniAOD_cff.py`  
  MiniAOD bad global muon tagging sequence.  It adapts the same cleaning logic
  to slimmed muon collections.

- `python/badGlobalMuonTaggerFWLite.py`  
  FWLite helper implementation for bad global muon tagging.  It is useful when
  comparing framework and lightweight analysis workflows.

- `python/chargedHadronTrackResolutionFilter_cfi.py`  
  Configures the charged hadron track-resolution filter.  It protects MET from
  charged candidates with badly measured tracks.

- `python/greedyMuonPFCandidateFilter_cfi.py`  
  Configures the greedy muon PF candidate filter.  It targets PF-muon matching
  pathologies.

- `python/inconsistentMuonPFCandidateFilter_cfi.py`  
  Configures the inconsistent muon PF candidate filter.  It removes events where
  PF and muon reconstruction disagree.

- `python/muonBadTrackFilter_cfi.py`  
  Configures the muon bad-track filter.  It catches muon-track pathologies that
  can fake large MET.

- `python/CSCTightHaloFilter_cfi.py`  
  Configures the CSC tight halo filter.  It points the filter at the beam-halo
  summary information needed for the CSC decision.

- `python/CSCTightHalo2015Filter_cfi.py`  
  Configures the 2015 CSC tight halo filter.  It preserves the historical
  2015-era halo recommendation.

- `python/CSCTightHaloTrkMuUnvetoFilter_cfi.py`  
  Configures the CSC tight halo filter without tracker-muon veto.  It is useful
  for studying the veto's impact.

- `python/globalTightHalo2016Filter_cfi.py`  
  Configures the 2016 global tight halo filter.  This is a common Run-2 MET
  filter recommendation.

- `python/globalSuperTightHalo2016Filter_cfi.py`  
  Configures the 2016 global super-tight halo filter.  It applies the stricter
  global halo decision.

- `python/HcalStripHaloFilter_cfi.py`  
  Configures the HCAL strip halo filter.  It targets HCAL energy patterns from
  beam halo.

- `python/EcalDeadCellTriggerPrimitiveFilter_cfi.py`  
  Configures the ECAL dead-cell trigger-primitive filter.  It defines the
  trigger primitive and rechit inputs used to identify missing ECAL response.

- `python/EcalDeadCellBoundaryEnergyFilter_cfi.py`  
  Configures the ECAL dead-cell boundary-energy filter.  It sets thresholds for
  energy around masked or dead ECAL cells.

- `python/ecalBadCalibFilter_cfi.py`  
  Configures the ECAL bad calibration filter.  It carries the bad-channel list
  and era modifiers for known problematic ECAL cells.

- `python/ecalLaserCorrFilter_cfi.py`  
  Configures the ECAL laser correction filter.  It uses laser-correction inputs
  to identify anomalous ECAL response.

- `python/eeBadScFilter_cfi.py`  
  Configures the EE bad-supercluster filter.  It targets problematic ECAL
  endcap superclusters.

- `python/eeNoiseFilter_cfi.py`  
  Configures the EE noise filter.  It targets ECAL endcap noise patterns.

- `python/hcalLaserEventFilter_cfi.py`  
  Configures the HCAL laser event filter.  It loads bad-event lists and applies
  era-dependent settings.

- `python/hcalLaserBadEvents_2011.py`  
  Python copy of the 2011 HCAL laser bad-event list.  It is imported by the HCAL
  laser filter configuration.

- `python/GenerateHcalLaserBadRunList.py`  
  Helper script for generating HCAL laser bad-run/event lists.  It is utility
  code rather than an event filter module.

- `python/primaryVertexFilter_cfi.py`  
  Configures the good primary vertex filter.  A valid collision vertex is a
  basic prerequisite for most MET analyses.

- `python/scrapingFilter_cfi.py`  
  Configures the scraping filter.  It removes beam-scraping-like events that can
  contaminate MET distributions.

- `python/trackingFailureFilter_cfi.py`  
  Configures the tracking failure filter.  It protects PF MET from global
  tracking reconstruction failures.

- `python/trackingPOGFilters_cfi.py`  
  Defines individual Tracking POG filter configurations.  These cover standard
  tracking event-quality requirements.

- `python/trackingPOGFilters_cff.py`  
  Combines Tracking POG filters into recommended sequences.  This is the
  sequence-level entry point for tracking-related MET cleaning.

- `python/jetIDFailureFilter_cfi.py`  
  Configures the jet ID failure filter.  It catches events where bad jets can
  dominate fake MET.

- `python/multiEventFilter_cfi.py`  
  Configures the multi-event utility filter.  It is used for event-list based
  tests and selections.

- `python/metFilters_cff.py`  
  Combines MET filter configurations into a standard sequence.  This is the
  main python lookup for standard MET filter bundles.

- `test/filters_cfg.py`  
  General test configuration for MET filters.  It shows how multiple filters can
  be run in a cmsRun process.

- `test/exampleRecommendation_cfg.py`  
  Example configuration for a standard MET filter recommendation.  It is a good
  reference for realistic filter placement.

- `test/exampleICHEPrecommendation_cfg.py`  
  Example configuration for the ICHEP-era MET filter recommendation.  It
  preserves an older recommended filter set.

- `test/test_badMuonCandidateFilter.py`  
  Focused test for bad PF muon filtering.  It is useful for reproducing
  muon-driven fake-MET cleaning behavior.

- `test/test_badChargedCandidateFilter.py`  
  Focused test for bad charged candidate filtering.  It is useful for
  reproducing charged-candidate fake-MET cleaning behavior.

## METPUSubtraction

**Role:** algorithms and producers for pileup-mitigated MET beyond the basic PF
MET sequence.

```text
METPUSubtraction/
|-- BuildFile.xml
|-- interface/
|   |-- DeepMETHelp.h
|   |-- MvaMEtUtilities.h
|   |-- NoPileUpMEtAuxFunctions.h
|   |-- NoPileUpMEtUtilities.h
|   |-- PFMETAlgorithmMVA.h
|   `-- PFMEtSignInterfaceBase.h
|-- plugins/
|   |-- BuildFile.xml
|   |-- DeepMETProducer.cc
|   |-- DeepMETSonicProducer.cc
|   |-- JVFJetIdProducer.cc
|   |-- JVFJetIdProducer.h
|   |-- NoPileUpPFMEtProducer.cc
|   |-- NoPileUpPFMEtProducer.h
|   |-- PFMETProducerMVA.cc
|   `-- PFMETProducerMVA.h
|-- python/
|   |-- deepMETProducer_cff.py
|   |-- deepMETSonicProducer_cff.py
|   |-- mitigatedMETSequence_cff.py
|   |-- mvaPFMET_Data_cff.py
|   |-- mvaPFMET_cff.py
|   |-- mvaPFMET_leptons_cff.py
|   |-- mvaPFMET_leptons_cfi.py
|   |-- mvaPFMET_leptons_data_cff.py
|   |-- objectSelection_cff.py
|   |-- pfNoPUMET_cff.py
|   `-- pfNoPUchsMET_cff.py
|-- src/
|   |-- DeepMETHelper.cc
|   |-- MvaMEtUtilities.cc
|   |-- NoPileUpMEtAuxFunctions.cc
|   |-- NoPileUpMEtUtilities.cc
|   |-- PFMETAlgorithmMVA.cc
|   `-- PFMEtSignInterfaceBase.cc
`-- test/
    |-- mvaMETOnMiniAOD_cfg.py
    |-- testDeepMETSonic_cfg.py
    |-- testDeepMET_cfg.py
    |-- testMVAMetProducer.py
    `-- writeGBRForests_cfg.py
```

- `BuildFile.xml`  
  Build dependencies for pileup-subtracted MET libraries and plugins.  It
  includes dependencies for MVA tools, TensorFlow/Triton-related producers, PF
  candidates, jets, and MET data formats.

- `interface/PFMETAlgorithmMVA.h` / `src/PFMETAlgorithmMVA.cc`  
  Core MVA MET algorithm.  It combines leptons, jets, PF candidates, pileup
  information, and trained regressors to estimate a pileup-mitigated MET vector.

- `interface/MvaMEtUtilities.h` / `src/MvaMEtUtilities.cc`  
  Utility functions for MVA MET object handling and kinematic calculations.  It
  keeps common calculations out of the producer implementation.

- `interface/NoPileUpMEtUtilities.h` / `src/NoPileUpMEtUtilities.cc`  
  Utilities for no-pileup MET.  These classify and combine event components so
  pileup contributions can be separated from hard-scatter contributions.

- `interface/NoPileUpMEtAuxFunctions.h` / `src/NoPileUpMEtAuxFunctions.cc`  
  Auxiliary types and helper functions for no-pileup MET, including candidate
  and vertex association structures.  These support the object bookkeeping
  needed for pileup subtraction.

- `interface/PFMEtSignInterfaceBase.h` / `src/PFMEtSignInterfaceBase.cc`  
  Interface base for PF MET significance-like calculations in the pileup
  subtraction context.  It connects no-pileup/MVA machinery with significance
  style covariance handling.

- `interface/DeepMETHelp.h` / `src/DeepMETHelper.cc`  
  Helper constants and preprocessing functions for DeepMET inputs.  It defines
  PF candidate feature scaling, outlier handling, and categorical embeddings
  used by the neural-network producers.

- `plugins/PFMETProducerMVA.h` / `plugins/PFMETProducerMVA.cc`  
  CMSSW producer for MVA MET.  It reads selected leptons, jets, PF candidates,
  and pileup information, then writes the MVA-corrected MET product.

- `plugins/NoPileUpPFMEtProducer.h` / `plugins/NoPileUpPFMEtProducer.cc`  
  Producer for no-pileup PF MET.  It separates event activity into hard-scatter
  and pileup components and constructs a pileup-mitigated MET vector.

- `plugins/JVFJetIdProducer.h` / `plugins/JVFJetIdProducer.cc`  
  Produces jet-vertex-fraction based jet IDs.  JVF is used to classify jets as
  hard-scatter-like or pileup-like for no-pileup/MVA MET.

- `plugins/DeepMETProducer.cc`  
  TensorFlow-based DeepMET producer.  It turns packed PF candidates into neural
  network tensors and writes PAT MET from the network-predicted missing px, py.

- `plugins/DeepMETSonicProducer.cc`  
  SONIC/Triton version of DeepMET inference.  It sends DeepMET inputs to an
  external inference service instead of running a local TensorFlow graph.

- `plugins/BuildFile.xml`  
  Plugin build dependencies for the pileup-subtraction producers.

- `python/objectSelection_cff.py`  
  Defines object selections used by MVA and mitigated MET sequences.  It is the
  first python file to inspect when wondering which leptons or jets enter MVA
  MET.

- `python/mvaPFMET_leptons_cfi.py`  
  Configures lepton inputs for MVA PF MET.  It defines the producer inputs for
  electron, muon, tau, and photon-like objects used in the regression.

- `python/mvaPFMET_leptons_cff.py`  
  Lepton-selection sequence for simulation-oriented MVA MET workflows.  It
  prepares object collections consumed by `PFMETProducerMVA`.

- `python/mvaPFMET_leptons_data_cff.py`  
  Lepton-selection sequence for data-oriented MVA MET workflows.  It adapts the
  lepton inputs for data processing.

- `python/mvaPFMET_cff.py`  
  Full MVA PF MET sequence for simulation.  It configures jet corrections, MVA
  weight files, and the `PFMETProducerMVA` module.

- `python/mvaPFMET_Data_cff.py`  
  Full MVA PF MET sequence for data.  It configures data-oriented corrections,
  MVA weight files, and the `PFMETProducerMVA` module.

- `python/pfNoPUMET_cff.py`  
  No-pileup PF MET sequence configuration.  It builds candidate, jet, JVF, and
  correction components for no-pileup MET.

- `python/pfNoPUchsMET_cff.py`  
  Charged-hadron-subtraction variant of no-pileup PF MET.  It adapts the no-PU
  workflow to CHS-style inputs.

- `python/mitigatedMETSequence_cff.py`  
  Combined mitigated MET sequence.  It assembles MVA MET and no-pileup MET
  components into a single higher-level workflow.

- `python/deepMETProducer_cff.py`  
  Configures DeepMET resolution-tune and response-tune producers, including
  era-dependent model paths.  It can swap local TensorFlow inference for Triton
  inference through the `deepMETSonicTriton` process modifier.

- `python/deepMETSonicProducer_cff.py`  
  Base configuration for the SONIC/Triton DeepMET producer.  It defines the
  inference-client settings used when DeepMET runs through Triton.

- `test/testMVAMetProducer.py`  
  Test configuration for MVA MET production.  It is a useful technical entry
  point after reading the MVA python fragments.

- `test/mvaMETOnMiniAOD_cfg.py`  
  Example configuration for running MVA MET on MiniAOD.  It shows the MiniAOD
  inputs needed by the MVA MET workflow.

- `test/testDeepMET_cfg.py`  
  Test configuration for local TensorFlow DeepMET.  It shows the minimal process
  setup for neural-network MET inference.

- `test/testDeepMETSonic_cfg.py`  
  Test configuration for SONIC/Triton DeepMET.  It shows the remote-inference
  process setup for DeepMET.

- `test/writeGBRForests_cfg.py`  
  Helper configuration for writing gradient-boosted regression forests used by
  MVA MET.  It is part of the model/weight preparation workflow rather than
  routine event reconstruction.

## Practical Debugging Guide

- If a MET collection is missing, start in `Configuration/python/*_cff.py` to
  see whether the producer is scheduled, then inspect the matching
  `METProducers/python/*_cfi.py` input tags.

- If a MET value is surprising, inspect the corresponding producer in
  `METProducers/src/` and then the algorithm in `METAlgorithms/src/`.  For PF
  MET, start from `PFMETProducer` and `PFSpecificAlgo`; for CaloMET, start from
  `CaloMETProducer` and `CaloSpecificAlgo`.

- If MET is large only in a few bad events, inspect `METFilters` first.  Bad
  muons, bad charged candidates, ECAL dead/bad cells, HCAL laser/noise, beam
  halo, and tracking failures are common fake-MET sources.

- If pileup mitigation or machine-learning MET is involved, inspect
  `METPUSubtraction/python/` first to understand the configured sequence and
  model files, then inspect the matching plugin and utility code.
