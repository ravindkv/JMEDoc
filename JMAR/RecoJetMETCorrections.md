# RecoJetMETCorrections package map

This directory is the `JetMETCorrections` CMSSW package. From the physics point
of view, it is the bridge between calibration payloads in conditions data and
the reconstructed physics objects used in analyses: corrected jets, corrected
MET, jet-energy-resolution objects, quark/gluon likelihood payload access, and
several legacy calibration or validation workflows.

Generated files such as `__pycache__/*.pyc` are intentionally omitted.

## Recommended learning order

Start with this order if the goal is to understand the physics first and the
technical details later:

1. `Configuration`
   - This is the best entry point. It shows the named JEC chains used in CMSSW:
     L1 pileup/offset, L2 relative eta response, L3 absolute pT response,
     residual data corrections, and L6 semileptonic-b corrections.
   - Read `python/JetCorrectors_cff.py`, then `python/CorrectedJetProducers_cff.py`.

2. `Algorithms`
   - This contains the actual per-jet correction implementations used by the
     producer modules. It is where the physics variables such as raw jet pT,
     eta, area, rho, NPV, EMF, and semileptonic-b lepton content enter the
     `FactorizedJetCorrectorCalculator`.

3. `Modules`
   - This turns correction algorithms into CMSSW modules and corrected jet
     collections. It also contains the JER and quark/gluon likelihood ESProducer
     access points.

4. `JetCorrector` and `Objects`
   - These provide the small runtime wrapper (`reco::JetCorrector`) and the
     EventSetup records (`JetCorrectionsRecord`, `METCorrectionsRecord`,
     `MEtXYcorrectRecord`) used to retrieve calibration payloads.

5. `Type1MET`
   - Read after the jet correction chain is clear. MET corrections propagate
     jet-energy corrections, unclustered-energy corrections, type-0 pileup
     corrections, muon corrections, and XY/phi corrections into MET.

6. `MCJet`
   - Use this for the calibration derivation/validation viewpoint. It contains
     truth-tree producers and utilities for L2/L3 response fits.

7. `FFTJetObjects`, `FFTJetModules`, and `InterpolationTables`
   - These are specialized FFTJet correction infrastructure and supporting
     interpolation/table code. They are useful, but not the first stop for
     standard AK4/AK8 JEC or MET debugging.

8. Legacy/specialized packages: `TauJet`, `JetVertexAssociation`, `MinBias`,
   and `IsolatedParticles`.
   - These are older or specialized correction/validation workflows. Read them
     when debugging those specific areas.

## Physics hierarchy

```text
JetMETCorrections
|-- Configuration         # Python definitions of JEC chains and corrected jet collections
|-- Algorithms            # C++ implementations of individual JEC levels
|-- Modules               # CMSSW producers/analyzers for JEC, JER, QG likelihood, corrected jets
|-- JetCorrector          # reco::JetCorrector wrapper and helper plugin
|-- Objects               # EventSetup records for JEC/MET correction payloads
|-- Type1MET              # Propagation of corrections into Calo/PF/PAT MET
|-- MCJet                 # MC-truth response trees and L2/L3 calibration utilities
|-- FFTJetObjects         # FFTJet correction object model and EventSetup loaders
|-- FFTJetModules         # FFTJet ESProducers and DB read/write modules
|-- InterpolationTables   # Generic multidimensional interpolation and table storage code
|-- TauJet                # Legacy tau-jet correction configuration and example
|-- JetVertexAssociation  # Legacy jet-vertex association code
|-- MinBias               # Legacy min-bias correction/validation code
`-- IsolatedParticles     # Test analyzers for isolated-track studies
```

## Algorithms

Tree:

```text
Algorithms
|-- BuildFile.xml
|-- ChangeLog
|-- interface
|   |-- JetCorrectorImplMakerBase.h
|   |-- L1FastjetCorrectorImpl.h
|   |-- L1JPTOffsetCorrectorImpl.h
|   |-- L1OffsetCorrectorImpl.h
|   |-- L6SLBCorrectorImpl.h
|   `-- LXXXCorrectorImpl.h
`-- src
    |-- JetCorrectorImplMakerBase.cc
    |-- L1FastjetCorrectorImpl.cc
    |-- L1JPTOffsetCorrectorImpl.cc
    |-- L1OffsetCorrectorImpl.cc
    |-- L6SLBCorrectorImpl.cc
    `-- LXXXCorrectorImpl.cc
```

| File | Description |
| --- | --- |
| `BuildFile.xml` | Declares the CMSSW build dependencies for the correction algorithm library. Inspect this when a compile or plugin dependency changes. |
| `ChangeLog` | Historical package notes. Useful mainly for understanding old implementation choices or migrations. |
| `interface/JetCorrectorImplMakerBase.h` | Base helper used by concrete corrector makers to retrieve `JetCorrectorParametersCollection` payloads from `JetCorrectionsRecord`. This is the common EventSetup/payload access layer for the algorithm implementations. |
| `src/JetCorrectorImplMakerBase.cc` | Implements payload token setup and calculator construction from the configured algorithm label and correction level. Read this to understand how a Python `algorithm` and `level` become a `FactorizedJetCorrectorCalculator`. |
| `interface/L1FastjetCorrectorImpl.h` | Interface for the L1FastJet correction implementation. Physics inputs are jet area, eta, pT, and event rho for pileup-density subtraction. |
| `src/L1FastjetCorrectorImpl.cc` | Implements L1FastJet by pulling rho from the event and evaluating the L1FastJet payload. This is the main code path for area-based pileup corrections. |
| `interface/L1OffsetCorrectorImpl.h` | Interface for the older L1Offset correction. It uses the number of reconstructed primary vertices instead of rho/area. |
| `src/L1OffsetCorrectorImpl.cc` | Implements the NPV-based L1Offset correction and checks that the configured payload level is `L1Offset`. Relevant when debugging legacy non-FastJet pileup corrections. |
| `interface/L1JPTOffsetCorrectorImpl.h` | Interface for JPT-specific L1 offset corrections. It can combine a JPT offset correction with an offset service from Calo jets. |
| `src/L1JPTOffsetCorrectorImpl.cc` | Implements the JPT offset correction path and optional offset-service handling. This is specialized legacy support for Jet-Plus-Track jets. |
| `interface/LXXXCorrectorImpl.h` | Generic implementation for standard named JEC levels such as L2Relative, L3Absolute, L2L3Residual, L4EMF, and similar factorized levels. This is the central non-L1 JEC algorithm interface. |
| `src/LXXXCorrectorImpl.cc` | Evaluates the configured factorized correction level for either a four-vector or a concrete `reco::Jet`. It maps payload level names to the calculator input variables and applies special CaloJet checks where needed. |
| `interface/L6SLBCorrectorImpl.h` | Interface for L6 semileptonic-b corrections. It adds b-tag/lepton information to the correction calculation for b jets with semileptonic decays. |
| `src/L6SLBCorrectorImpl.cc` | Implements L6SLB by reading soft-muon/soft-electron tag info and evaluating the L6 payload. Read this only after the standard L1-L3 chain is clear. |

## Configuration

Tree:

```text
Configuration
|-- ChangeLog
|-- data
|   |-- CMSSW_167_TrackLeakage.txt
|   |-- CMSSW_167_TrackLeakage_one.txt
|   |-- CMSSW_167_TrackNonEff.txt
|   |-- CMSSW_167_TrackNonEffLeakage.txt
|   |-- CMSSW_167_TrackNonEffLeakage_One.txt
|   |-- CMSSW_167_TrackNonEff_PTDR.txt
|   |-- CMSSW_167_TrackNonEff_Resp_one.txt
|   |-- CMSSW_167_TrackNonEff_one.txt
|   |-- CMSSW_167_response.txt
|   |-- CMSSW_31X_resptowers.txt
|   |-- CMSSW_340_TrackNonEff.txt
|   `-- CMSSW_340_response.txt
|-- python
|   |-- CorrectedJetProducersAllAlgos_cff.py
|   |-- CorrectedJetProducersDefault_cff.py
|   |-- CorrectedJetProducers_cff.py
|   |-- JetCorrectionCondDB_cff.py
|   |-- JetCorrectorsAllAlgos_cff.py
|   |-- JetCorrectorsForReco_cff.py
|   |-- JetCorrectors_cff.py
|   `-- SLBTagging_cff.py
`-- test
    |-- jetAODSkim_HLT_DiJetAve15_cfg.py
    |-- jetAODSkim_HLT_DiJetAve30_cfg.py
    |-- run_ak5L2L3_cfg.py
    |-- run_default_cfg.py
    `-- run_kt4L2L3_cfg.py
```

| File | Description |
| --- | --- |
| `ChangeLog` | Historical notes for the configuration package. Useful when interpreting old era-specific names. |
| `python/JetCorrectors_cff.py` | Main configuration file for standard AK4 corrector modules and chains. Start here to understand how L1Offset, L1FastJet, L2Relative, L3Absolute, residual, L6SLB, and chained correctors are named. |
| `python/JetCorrectorsAllAlgos_cff.py` | Extends the AK4 patterns to many algorithms and radii: AK, KT, IC, Calo, PF, PFCHS, JPT, Track, and legacy Gen/Calo/PF combinations. Use this for debugging non-default jet collections. |
| `python/JetCorrectorsForReco_cff.py` | Minimal corrector sequence imported by reconstruction for AK4 PF and PFCHS L1FastL2L3 chains. This is a compact entry point for standard reco-era JEC. |
| `python/CorrectedJetProducers_cff.py` | Defines corrected jet EDProducers for AK4 Calo, PF, PFCHS, JPT, and Track jets at L1/L2/L2L3/L1L2L3/L6 combinations. Shows how corrector labels are attached to jet collections. |
| `python/CorrectedJetProducersDefault_cff.py` | Defines a broader default set of corrected jet collections for common algorithms and residual variants. Useful for full validation jobs or older workflows. |
| `python/CorrectedJetProducersAllAlgos_cff.py` | Expands corrected jet producers to many algorithms and jet radii. Use when comparing behavior across jet clustering choices. |
| `python/JetCorrectionCondDB_cff.py` | Example configuration for reading JEC payloads from a local conditions database. Useful when testing private SQLite payloads instead of the GlobalTag. |
| `python/SLBTagging_cff.py` | Defines soft-lepton b-tagging tag-info producers needed by L6 semileptonic-b corrections. Read together with `Algorithms/L6SLBCorrectorImpl`. |
| `data/CMSSW_167_response.txt` | Legacy text table for jet response corrections in an old CMSSW release. It is calibration input/reference material, not a modern central payload. |
| `data/CMSSW_167_TrackNonEff.txt` | Legacy tracking inefficiency correction table. It documents old track-based correction studies. |
| `data/CMSSW_167_TrackNonEff_one.txt` | Single-variant version of the old tracking inefficiency table. Useful only for reproducing old validation configurations. |
| `data/CMSSW_167_TrackNonEff_Resp_one.txt` | Legacy combined tracking inefficiency and response table. It appears to support old one-scenario correction tests. |
| `data/CMSSW_167_TrackNonEff_PTDR.txt` | Legacy PTDR-era tracking inefficiency table. Keep as historical calibration reference. |
| `data/CMSSW_167_TrackNonEffLeakage.txt` | Legacy table combining track inefficiency and leakage effects. Relevant only to old jet response studies. |
| `data/CMSSW_167_TrackNonEffLeakage_One.txt` | Single-scenario version of the legacy inefficiency/leakage table. Useful for old reproductions. |
| `data/CMSSW_167_TrackLeakage.txt` | Legacy table for track leakage effects. It is not part of the modern factorized JEC chain. |
| `data/CMSSW_167_TrackLeakage_one.txt` | Single-scenario track leakage table for old tests. |
| `data/CMSSW_31X_resptowers.txt` | Legacy response table for calorimeter towers in the 31X era. Mostly useful for historical comparisons. |
| `data/CMSSW_340_response.txt` | Legacy response table from the 340 era. It documents older calibration inputs. |
| `data/CMSSW_340_TrackNonEff.txt` | Legacy track inefficiency table from the 340 era. |
| `test/run_default_cfg.py` | Test job that loads default corrected jet producers and histograms selected corrected collections. Useful for checking that chains run in a CMSSW process. |
| `test/run_ak5L2L3_cfg.py` | Legacy AK5 L2L3 correction validation/test configuration. Useful when reproducing older JEC behavior. |
| `test/run_kt4L2L3_cfg.py` | KT4 L2L3 correction validation/test configuration. Useful for non-AK algorithm checks. |
| `test/jetAODSkim_HLT_DiJetAve15_cfg.py` | AOD skim configuration for dijet-average trigger studies at a lower threshold. This supports JEC validation samples. |
| `test/jetAODSkim_HLT_DiJetAve30_cfg.py` | AOD skim configuration for dijet-average trigger studies at a higher threshold. This supports response and balance studies. |

## Modules

Tree:

```text
Modules
|-- BuildFile.xml
|-- ChangeLog
|-- interface
|   |-- CorrectedJetProducer.h
|   |-- JetResolution.h
|   `-- JetResolutionESProducer.h
|-- plugins
|   |-- BuildFile.xml
|   |-- ChainedJetCorrectorProducer.cc
|   |-- CorrectedJetProducers.cc
|   |-- FactorizedJetCorrectorDemo.cc
|   |-- JetCorrectorDemo.cc
|   |-- JetCorrectorOnTheFly.cc
|   |-- JetCorrectorProducer.h
|   |-- JetCorrectorProducers.cc
|   |-- JetResolutionDemo.cc
|   |-- QGLikelihoodESProducer.cc
|   |-- QGLikelihoodSystematicsESProducer.cc
|   `-- SealModule.cc
|-- python
|   |-- JetResolutionESProducer_cfi.py
|   `-- qglESProducer_cfi.py
|-- src
|   |-- JetResolution.cc
|   |-- classes.h
|   `-- classes_def.xml
`-- test
    |-- BuildFile.xml
    |-- FactorizedJetCorrectorDemoLocal_cfg.py
    |-- JetCorrectionDBReader_cfg.py
    |-- JetCorrectionDBWriter_cfg.py
    |-- JetCorrectionLocalDBReader_cfg.py
    |-- JetCorrectionPrepTestDBReader_cfg.py
    |-- JetCorrectionProdTestDBReader_cfg.py
    |-- JetCorrectorDemoLocal_cfg.py
    |-- JetCorrectorDemoPrep_cfg.py
    |-- JetCorrectorDemo_cfg.py
    |-- JetCorrectorOnTheFly_cfg.py
    |-- JetResolutionDBWriter_cfg.py
    |-- JetResolutionDemo_cfg.py
    |-- JetResolutionLocalDBReader_cfg.py
    |-- METCorrectionDBWriter_cfg.py
    |-- METCorrectionLocalDBReader_cfg.py
    |-- QGLikelihoodDBWriter_cfg.py
    |-- QGLikelihoodLocalDBReader_cfg.py
    |-- README
    |-- TauJetCorrectionDBReader_cfg.py
    |-- TauJetCorrectionDBWriter_cfg.py
    |-- testAllIOVs.py
    |-- testJEC_cfg.py
    |-- test_jetresolution.sh
    `-- uploadConstants.py
```

| File | Description |
| --- | --- |
| `BuildFile.xml` | Build rules for the central CMSSW modules library. It connects framework, data formats, conditions, and ROOT dependencies. |
| `ChangeLog` | Historical notes for module changes. Useful when interpreting older test configurations. |
| `interface/CorrectedJetProducer.h` | Template EDProducer that applies one or more `reco::JetCorrector` objects to an input jet collection and writes corrected jets. This is where correction factors become corrected jet four-vectors. |
| `interface/JetResolution.h` | Public JER/JER scale-factor API wrappers in namespace `JME`. It provides parameter objects and methods to evaluate resolution and scale factors from payload records or text files. |
| `src/JetResolution.cc` | Implements JER text/payload loading, parameter matching, and resolution/scale-factor evaluation. Read this for how eta, pT, rho, and other variables map onto JER bins. |
| `interface/JetResolutionESProducer.h` | ESProducer templates for serving JER and JER scale-factor objects from conditions records. This is the EventSetup access point for JER payloads. |
| `src/classes.h` | ROOT dictionary helper for JER-related classes. It makes the data structures persistable where needed. |
| `src/classes_def.xml` | Dictionary selection file for the classes in `classes.h`. |
| `plugins/JetCorrectorProducer.h` | Template producer that creates event-level `reco::JetCorrector` products from the algorithm implementations in `Algorithms`. It is the generic bridge from implementation class to CMSSW EDProducer. |
| `plugins/JetCorrectorProducers.cc` | Registers the concrete producers: `LXXXCorrectorProducer`, `L1OffsetCorrectorProducer`, `L1JPTOffsetCorrectorProducer`, `L1FastjetCorrectorProducer`, and `L6SLBCorrectorProducer`. |
| `plugins/ChainedJetCorrectorProducer.cc` | Produces a `reco::JetCorrector` that multiplies a configured list of correction factors in order. This represents the physics chain such as L1FastJet * L2Relative * L3Absolute * Residual. |
| `plugins/CorrectedJetProducers.cc` | Registers concrete corrected jet producers for Calo, PF, JPT, Track, and Gen jets. These are the modules referenced by `Configuration/python/CorrectedJetProducers*.py`. |
| `plugins/JetCorrectorDemo.cc` | Analyzer demonstrating use of a `reco::JetCorrector` and JEC uncertainty payloads. Useful as a worked example for plotting correction factors and uncertainties. |
| `plugins/FactorizedJetCorrectorDemo.cc` | Analyzer demonstrating direct use of `FactorizedJetCorrector` from payload levels. Good for understanding the factorized correction calculator outside the normal producer chain. |
| `plugins/JetCorrectorOnTheFly.cc` | Analyzer that applies a corrector to jets during analysis rather than producing a corrected collection. Useful for debugging correction factors on selected jets. |
| `plugins/JetResolutionDemo.cc` | Analyzer demonstrating JER and JER scale-factor usage. It shows both text-file and EventSetup access patterns and produces diagnostic histograms. |
| `plugins/QGLikelihoodESProducer.cc` | EventSetup producer that exposes a `QGLikelihoodObject` from `QGLikelihoodRcd`. Relevant for quark/gluon discriminator payload access. |
| `plugins/QGLikelihoodSystematicsESProducer.cc` | EventSetup producer for `QGLikelihoodSystematicsObject` from `QGLikelihoodSystematicsRcd`. Used for QG likelihood systematic payloads. |
| `plugins/SealModule.cc` | Registers JER ESProducer modules. This is framework glue rather than physics logic. |
| `plugins/BuildFile.xml` | Build rules for the plugin library. Inspect when plugin registration or dependencies fail. |
| `python/JetResolutionESProducer_cfi.py` | Default configuration for AK4PFchs JER and JER scale-factor ESProducers. Start here when an analysis needs JER payloads from conditions. |
| `python/qglESProducer_cfi.py` | Default configuration for QG likelihood ESProducers for AK5PF and AK5PFchs labels. |
| `test/README` | Notes for the module test area. Read before running old DB read/write tests. |
| `test/testJEC_cfg.py` | Simple JEC test job with a local GlobalTag override. Useful for smoke-testing corrected jet production. |
| `test/JetCorrectorDemo_cfg.py` | Configuration for the `JetCorrectorDemo` analyzer using standard payload access. |
| `test/JetCorrectorDemoLocal_cfg.py` | Local-payload version of the JEC demo. Use this for SQLite/text payload debugging. |
| `test/JetCorrectorDemoPrep_cfg.py` | Preparation configuration for the JEC demo workflow. |
| `test/FactorizedJetCorrectorDemoLocal_cfg.py` | Local-payload configuration for direct factorized JEC evaluation. |
| `test/JetCorrectorOnTheFly_cfg.py` | Test configuration for applying JEC during analysis rather than producing corrected collections. |
| `test/JetCorrectionDBWriter_cfg.py` | Writes JEC payloads into a conditions database. Useful for payload production tests. |
| `test/JetCorrectionDBReader_cfg.py` | Reads JEC payloads from a database and validates retrieval. |
| `test/JetCorrectionLocalDBReader_cfg.py` | Local SQLite reader configuration for JEC payload checks. |
| `test/JetCorrectionPrepTestDBReader_cfg.py` | Pre-production JEC database reader test. |
| `test/JetCorrectionProdTestDBReader_cfg.py` | Production-style JEC database reader test. |
| `test/JetResolutionDemo_cfg.py` | Runs the JER demo analyzer. Useful for checking resolution and scale-factor payloads. |
| `test/JetResolutionDBWriter_cfg.py` | Writes JER payloads to a database for testing. |
| `test/JetResolutionLocalDBReader_cfg.py` | Reads JER payloads from a local database. |
| `test/test_jetresolution.sh` | Shell regression test for JER payload access or demo execution. |
| `test/METCorrectionDBWriter_cfg.py` | Writes MET correction payloads, especially XY correction payloads, into a DB. |
| `test/METCorrectionLocalDBReader_cfg.py` | Reads MET correction payloads from a local DB. |
| `test/QGLikelihoodDBWriter_cfg.py` | Writes QG likelihood payloads to a conditions DB. |
| `test/QGLikelihoodLocalDBReader_cfg.py` | Reads QG likelihood payloads from a local DB. |
| `test/TauJetCorrectionDBWriter_cfg.py` | Writes tau-jet correction payloads to a DB for legacy tau-jet workflows. |
| `test/TauJetCorrectionDBReader_cfg.py` | Reads tau-jet correction payloads from a DB. |
| `test/testAllIOVs.py` | Helper script to run tests over all intervals of validity. Useful for broad payload validation. |
| `test/uploadConstants.py` | Helper script for uploading constants/payload files. Check carefully before using because it interfaces with payload publication workflows. |
| `test/BuildFile.xml` | Build rules for test analyzers/scripts. |

## JetCorrector

Tree:

```text
JetCorrector
|-- BuildFile.xml
|-- interface
|   |-- JetCorrector.h
|   `-- JetCorrectorImpl.h
|-- plugins
|   |-- BuildFile.xml
|   `-- JetTracksAssociationToTrackRefs.cc
`-- src
    |-- JetCorrector.cc
    |-- JetCorrectorImpl.cc
    |-- classes.h
    `-- classes_def.xml
```

| File | Description |
| --- | --- |
| `BuildFile.xml` | Build rules for the lightweight jet-corrector wrapper package. |
| `interface/JetCorrector.h` | Public wrapper class around a `JetCorrectorImpl`. Client code asks this object for correction factors. |
| `src/JetCorrector.cc` | Implements wrapper forwarding to the underlying implementation. This keeps module code independent of the concrete correction algorithm. |
| `interface/JetCorrectorImpl.h` | Abstract interface for all jet-correction implementations. It defines correction methods for four-vectors, jets, and jets with references. |
| `src/JetCorrectorImpl.cc` | Base implementation details for the abstract interface. Most physics behavior is in derived classes under `Algorithms`. |
| `plugins/JetTracksAssociationToTrackRefs.cc` | Helper producer converting jet-track associations into track references. This supports legacy track/JPT workflows rather than standard PF JEC. |
| `plugins/BuildFile.xml` | Build rules for the helper plugin. |
| `src/classes.h` | ROOT dictionary helper for `reco::JetCorrector`. |
| `src/classes_def.xml` | Dictionary selection for `reco::JetCorrector` wrapper persistence metadata. |

## Objects

Tree:

```text
Objects
|-- BuildFile.xml
|-- ChangeLog
|-- interface
|   |-- JetCorrectionsRecord.h
|   |-- METCorrectionsRecord.h
|   `-- MEtXYcorrectRecord.h
`-- src
    |-- JetCorrectionsRecord.cc
    |-- METCorrectionsRecord.cc
    `-- MEtXYcorrectRecord.cc
```

| File | Description |
| --- | --- |
| `BuildFile.xml` | Build rules for correction EventSetup records. |
| `ChangeLog` | Historical notes for record definitions. |
| `interface/JetCorrectionsRecord.h` | EventSetup record declaration for JEC payload collections. Most JEC algorithms retrieve `JetCorrectorParametersCollection` through this record. |
| `src/JetCorrectionsRecord.cc` | Registers `JetCorrectionsRecord` with the framework. |
| `interface/METCorrectionsRecord.h` | EventSetup record declaration for MET correction payloads. Used by MET DB read/write and correction modules. |
| `src/METCorrectionsRecord.cc` | Registers `METCorrectionsRecord`. |
| `interface/MEtXYcorrectRecord.h` | EventSetup record declaration for MET XY/phi correction payloads. The mixed capitalization is historical. |
| `src/MEtXYcorrectRecord.cc` | Registers `MEtXYcorrectRecord`. |

## Type1MET

Tree:

```text
Type1MET
|-- BuildFile.xml
|-- data
|   |-- BareRootFunc.C
|   `-- FWLiteFunc.C
|-- interface
|   |-- AddCorrectionsToGenericMET.h
|   |-- CaloJetMETcorrInputProducerT.h
|   |-- JetCleanerForType1METT.h
|   |-- JetCorrExtractorT.h
|   |-- METCorrectionAlgorithm.h
|   `-- PFJetMETcorrInputProducerT.h
|-- plugins
|   |-- BadPFCandidateJetsEEnoiseProducer.cc
|   |-- BuildFile.xml
|   |-- CaloJetMETcorrInputProducer.cc
|   |-- CorrectedCaloMETProducer.cc
|   |-- CorrectedPFMETProducer.cc
|   |-- CorrectedPatMETProducer.cc
|   |-- JetCleanerForType1MET.cc
|   |-- MultShiftMETcorrDBInputProducer.cc
|   |-- MultShiftMETcorrDBInputProducer.h
|   |-- MultShiftMETcorrInputProducer.cc
|   |-- MultShiftMETcorrInputProducer.h
|   |-- MuonMETcorrInputProducer.cc
|   |-- MuonMETcorrInputProducer.h
|   |-- PFCandMETcorrInputProducer.cc
|   |-- PFCandMETcorrInputProducer.h
|   |-- PFJetMETcorrInputProducer.cc
|   |-- PFchsMETcorrInputProducer.cc
|   |-- PFchsMETcorrInputProducer.h
|   |-- ScaleCorrMETData.cc
|   |-- SysShiftMETcorrInputProducer.cc
|   |-- SysShiftMETcorrInputProducer.h
|   |-- Type0PFMETcorrInputProducer.cc
|   |-- Type0PFMETcorrInputProducer.h
|   |-- Type1PFMET.cc
|   |-- Type2CorrectionProducer.cc
|   `-- UnclusteredBlobProducer.cc
|-- python
|   |-- cleanJetFromEEnoise_cfi.py
|   |-- correctedMet_cff.py
|   |-- correctedPatMet_cff.py
|   |-- correctionTermsCaloMet_cff.py
|   |-- correctionTermsPfMetMultDB_cff.py
|   |-- correctionTermsPfMetMult_cff.py
|   |-- correctionTermsPfMetShiftXY_cff.py
|   |-- correctionTermsPfMetType0PFCandidate_cff.py
|   |-- correctionTermsPfMetType0RecoTrack_cff.py
|   |-- correctionTermsPfMetType1Type2_cff.py
|   |-- multPhiCorr_741_25nsDY_cfi.py
|   |-- multPhiCorr_741_50nsDY_cfi.py
|   |-- multPhiCorr_74X_50ns_cfi.py
|   |-- multPhiCorr_Puppi_Run2_ULDATA_cfi.py
|   |-- multPhiCorr_Puppi_Run2_ULMC_cfi.py
|   |-- multPhiCorr_Run2_EOYMC_cfi.py
|   |-- multPhiCorr_Run2_ULDATA_cfi.py
|   |-- multPhiCorr_Run2_ULMC_cfi.py
|   |-- multPhiCorr_phys14_cfi.py
|   |-- pfMETCorrectionType0_cfi.py
|   |-- pfMETmultShiftCorrectionsDB_cfi.py
|   |-- pfMETmultShiftCorrections_cfi.py
|   |-- pfMETsysShiftCorrections_cfi.py
|   `-- testInputFiles_cff.py
|-- src
|   |-- AddCorrectionsToGenericMET.cc
|   `-- METCorrectionAlgorithm.cc
`-- test
    |-- BuildFile.xml
    |-- corrMET_caloMet_cfg.py
    |-- corrMET_pfMet_cfg.py
    |-- runtests.sh
    |-- testMultShiftMETcorrDBInputProducer.py
    `-- testMultShiftMETcorrInputProducer.py
```

| File | Description |
| --- | --- |
| `BuildFile.xml` | Build rules for MET correction libraries and plugins. |
| `interface/METCorrectionAlgorithm.h` | Algorithm for summing one or more `CorrMETData` correction terms and applying them to a MET object. This is the central vector arithmetic for corrected MET. |
| `src/METCorrectionAlgorithm.cc` | Implements MET correction-vector summation and MET four-vector updates. Read this to see the sign conventions. |
| `interface/AddCorrectionsToGenericMET.h` | Generic helper for applying correction terms to MET-like objects. Used by the concrete Calo/PF/PAT MET producers. |
| `src/AddCorrectionsToGenericMET.cc` | Implements the generic correction application helper. |
| `interface/JetCorrExtractorT.h` | Template helper for extracting raw/corrected jet information and JEC factors for MET propagation. |
| `interface/PFJetMETcorrInputProducerT.h` | Template producer for computing PF jet-based MET correction terms. Physics role: propagate PF jet JEC changes into MET type-1/type-2 corrections. |
| `plugins/PFJetMETcorrInputProducer.cc` | Registers the PF jet MET correction input producer. This module builds `CorrMETData` from PF jets and JEC labels. |
| `interface/CaloJetMETcorrInputProducerT.h` | Template producer for Calo jet-based MET correction terms. Physics role: propagate Calo jet energy corrections into CaloMET. |
| `plugins/CaloJetMETcorrInputProducer.cc` | Registers the Calo jet MET correction input producer. |
| `interface/JetCleanerForType1METT.h` | Template jet-cleaning helper for type-1 MET. It removes jets overlapping with selected objects or failing quality criteria. |
| `plugins/JetCleanerForType1MET.cc` | Registers concrete jet-cleaner modules for type-1 MET workflows. |
| `plugins/CorrectedPFMETProducer.cc` | EDProducer that applies configured correction terms to PF MET. Main producer for full AOD PF MET corrections. |
| `plugins/CorrectedCaloMETProducer.cc` | EDProducer that applies configured correction terms to Calo MET. |
| `plugins/CorrectedPatMETProducer.cc` | EDProducer for corrected PAT/MiniAOD MET. It is the MiniAOD-facing counterpart of corrected PF MET production. |
| `plugins/Type1PFMET.cc` | Plugin for producing type-1 corrected PF MET in older workflows. Read alongside `correctionTermsPfMetType1Type2_cff.py`. |
| `plugins/Type2CorrectionProducer.cc` | Produces type-2/unclustered-energy correction terms from type-1 and particle-flow correction inputs. Physics role: handle recoil from unclustered energy. |
| `plugins/UnclusteredBlobProducer.cc` | Builds unclustered-energy blobs for MET uncertainty/correction workflows. |
| `plugins/PFCandMETcorrInputProducer.h` | Interface for producing MET correction terms from PF candidates not clustered into jets. |
| `plugins/PFCandMETcorrInputProducer.cc` | Implements PF-candidate-based unclustered correction inputs. |
| `plugins/MuonMETcorrInputProducer.h` | Interface for muon-related MET correction inputs. |
| `plugins/MuonMETcorrInputProducer.cc` | Produces MET correction terms from muon momentum corrections, especially important for CaloMET workflows. |
| `plugins/Type0PFMETcorrInputProducer.h` | Interface for type-0 PF MET correction inputs. Type-0 corrects charged pileup/recoil effects associated with vertices. |
| `plugins/Type0PFMETcorrInputProducer.cc` | Implements type-0 correction terms using PF-candidate to vertex associations and hard-scatter vertex selection. |
| `plugins/PFchsMETcorrInputProducer.h` | Interface for CHS-based type-0-like MET correction input. |
| `plugins/PFchsMETcorrInputProducer.cc` | Sums charged-hadron-subtraction information into a `CorrMETData` term. |
| `plugins/ScaleCorrMETData.cc` | Scales an existing `CorrMETData` term by configured factors. Useful for deriving related type-0/type-2 inputs. |
| `plugins/SysShiftMETcorrInputProducer.h` | Interface for run/Nvtx/sumEt parameterized XY shift corrections. |
| `plugins/SysShiftMETcorrInputProducer.cc` | Implements older systematic MET x/y shift correction from configured parameter sets. |
| `plugins/MultShiftMETcorrInputProducer.h` | Interface for multi-era/multi-sample MET XY correction from Python VPSet parameterizations. |
| `plugins/MultShiftMETcorrInputProducer.cc` | Implements MET phi/XY corrections using configured run-era and sample-dependent parameters. |
| `plugins/MultShiftMETcorrDBInputProducer.h` | Interface for MET XY corrections read from conditions DB payloads. |
| `plugins/MultShiftMETcorrDBInputProducer.cc` | Implements DB-backed MET XY corrections through `MEtXYcorrectRecord` payloads. |
| `plugins/BadPFCandidateJetsEEnoiseProducer.cc` | Identifies PF-candidate jets affected by endcap noise. Used in MiniAOD-style cleaning before unclustered-energy uncertainty handling. |
| `plugins/BuildFile.xml` | Build rules for MET correction plugins. |
| `python/correctionTermsPfMetType1Type2_cff.py` | Main PF MET correction-term configuration. It defines PF jet type-1 corrections, unclustered PF-candidate type-2 inputs, and the corrector chains used for MC/data. |
| `python/correctedMet_cff.py` | Defines concrete corrected Calo and PF MET collections for combinations of type-0, type-1, type-2, and XY corrections. |
| `python/correctedPatMet_cff.py` | Defines corrected PAT/MiniAOD MET, especially the DB-backed XY correction path for `slimmedMETs`. |
| `python/correctionTermsCaloMet_cff.py` | Defines CaloMET correction inputs: Calo jet type-1, muon correction, and type-2 unclustered correction. |
| `python/correctionTermsPfMetType0RecoTrack_cff.py` | Defines type-0 correction terms from CHS/reco-track style information. |
| `python/correctionTermsPfMetType0PFCandidate_cff.py` | Defines type-0 correction terms from PF candidate to vertex association. |
| `python/pfMETCorrectionType0_cfi.py` | Detailed type-0 PF MET setup: vertex selection, PF candidate association, displaced-vertex imports, and correction parameters. |
| `python/correctionTermsPfMetShiftXY_cff.py` | Sequence wrapper for the older system-shift XY correction producer. |
| `python/pfMETsysShiftCorrections_cfi.py` | Parameter sets for older MET x/y shifts versus sumEt or Nvtx for 2011/2012 data and MC. |
| `python/correctionTermsPfMetMult_cff.py` | Sequence wrapper for configured multi-era XY/phi corrections from Python parameter tables. |
| `python/pfMETmultShiftCorrections_cfi.py` | Configures `MultShiftMETcorrInputProducer` and imports legacy 25 ns/50 ns DY parameter tables. |
| `python/correctionTermsPfMetMultDB_cff.py` | Sequence wrapper for DB-backed multi-era XY/phi corrections. |
| `python/pfMETmultShiftCorrectionsDB_cfi.py` | Configures `MultShiftMETcorrDBInputProducer` for MiniAOD-like inputs and payload labels. |
| `python/cleanJetFromEEnoise_cfi.py` | MiniAOD cleaning sequence for bad endcap-noise PF candidates and unclustered-energy handling. |
| `python/multPhiCorr_phys14_cfi.py` | PHYS14-era MET phi/XY correction parameter table. Historical but useful for reproducing old samples. |
| `python/multPhiCorr_741_50nsDY_cfi.py` | 74X/741 50 ns DY MET phi/XY correction parameters. |
| `python/multPhiCorr_741_25nsDY_cfi.py` | 74X/741 25 ns DY MET phi/XY correction parameters. |
| `python/multPhiCorr_74X_50ns_cfi.py` | 74X 50 ns MET phi/XY correction parameter table. |
| `python/multPhiCorr_Run2_EOYMC_cfi.py` | Run 2 end-of-year MC MET phi/XY correction tables, including 2016/2017/2018 variants. |
| `python/multPhiCorr_Run2_ULMC_cfi.py` | Run 2 UltraLegacy MC MET phi/XY correction tables. |
| `python/multPhiCorr_Run2_ULDATA_cfi.py` | Run 2 UltraLegacy data MET phi/XY correction tables by era. |
| `python/multPhiCorr_Puppi_Run2_ULMC_cfi.py` | Run 2 UltraLegacy MC PUPPI MET phi/XY correction tables. |
| `python/multPhiCorr_Puppi_Run2_ULDATA_cfi.py` | Run 2 UltraLegacy data PUPPI MET phi/XY correction tables by era. |
| `python/testInputFiles_cff.py` | RelVal input-file helper for MET correction tests. |
| `data/BareRootFunc.C` | ROOT macro helper for standalone MET correction studies. |
| `data/FWLiteFunc.C` | FWLite-oriented ROOT macro helper for MET correction studies. |
| `test/corrMET_pfMet_cfg.py` | Test job exercising PF MET type-0/type-1/type-2/XY correction combinations. |
| `test/corrMET_caloMet_cfg.py` | Test job exercising CaloMET correction terms. |
| `test/testMultShiftMETcorrInputProducer.py` | Test for Python-configured multi-era XY shift corrections. |
| `test/testMultShiftMETcorrDBInputProducer.py` | Test for DB-backed multi-era XY shift corrections. |
| `test/runtests.sh` | Shell wrapper for MET correction tests. |
| `test/BuildFile.xml` | Build rules for MET correction tests. |

## MCJet

Tree:

```text
MCJet
|-- bin
|   |-- BuildFile.xml
|   |-- L2Correction.cc
|   |-- L3Correction.cc
|   |-- ReadTree.cc
|   |-- ResponseFitter.cc
|   `-- Utilities.h
|-- plugins
|   |-- BuildFile.xml
|   |-- CaloMCTruthTreeProducer.cc
|   |-- CaloMCTruthTreeProducer.h
|   |-- JetUtilMC.h
|   |-- PFMCTruthTreeProducer.cc
|   |-- PFMCTruthTreeProducer.h
|   `-- SealModule.cc
|-- python
|   `-- RelValQCD_cfi.py
`-- test
    |-- DrawDistributions.C
    |-- DrawL2.C
    |-- DrawL3.C
    |-- DrawL3Comparison.C
    |-- DrawResponse.C
    |-- DrawResponseVsEta.C
    |-- HistoSettings.conf
    |-- ReadTree.config
    |-- RunProduction.py
    |-- Settings.h
    `-- testMCTruthTree_cfg.py
```

| File | Description |
| --- | --- |
| `plugins/CaloMCTruthTreeProducer.h` | Interface for a truth-tree producer matching Calo jets to generated information. This supports response measurement for Calo JEC derivation. |
| `plugins/CaloMCTruthTreeProducer.cc` | Implements Calo jet truth-tree filling, including jet/gen matching and response variables. |
| `plugins/PFMCTruthTreeProducer.h` | Interface for PF jet truth-tree production. This is the PF analogue of the Calo response tree producer. |
| `plugins/PFMCTruthTreeProducer.cc` | Implements PF jet response tree filling against MC truth. |
| `plugins/JetUtilMC.h` | Shared MC matching and kinematic utility helpers for truth-tree producers. |
| `plugins/SealModule.cc` | Registers MC truth-tree producer plugins. |
| `plugins/BuildFile.xml` | Build rules for MCJet plugins. |
| `bin/ReadTree.cc` | Standalone utility for reading calibration trees and producing response inputs. |
| `bin/ResponseFitter.cc` | Standalone response-fitting utility. It is part of the calibration derivation workflow. |
| `bin/L2Correction.cc` | Utility for deriving or inspecting L2Relative eta-dependent correction behavior from response inputs. |
| `bin/L3Correction.cc` | Utility for deriving or inspecting L3Absolute pT-dependent correction behavior. |
| `bin/Utilities.h` | Shared helper functions for MCJet standalone utilities. |
| `bin/BuildFile.xml` | Build rules for MCJet executables. |
| `python/RelValQCD_cfi.py` | RelVal QCD input source configuration for MC truth-tree tests. |
| `test/testMCTruthTree_cfg.py` | CMSSW test configuration running Calo and PF MC truth-tree producers. |
| `test/RunProduction.py` | Helper script for running MCJet production workflows. |
| `test/ReadTree.config` | Configuration file for the `ReadTree` utility. |
| `test/HistoSettings.conf` | Histogram settings for response plotting macros. |
| `test/Settings.h` | Shared ROOT macro settings for MCJet response plots. |
| `test/DrawResponse.C` | ROOT macro for drawing jet response distributions. |
| `test/DrawResponseVsEta.C` | ROOT macro for drawing response versus eta, central to L2Relative studies. |
| `test/DrawL2.C` | ROOT macro for visualizing L2 correction behavior. |
| `test/DrawL3.C` | ROOT macro for visualizing L3 correction behavior. |
| `test/DrawL3Comparison.C` | ROOT macro comparing L3 correction variants. |
| `test/DrawDistributions.C` | ROOT macro for general calibration-tree distributions. |

## FFTJetObjects

Tree:

```text
FFTJetObjects
|-- BuildFile.xml
|-- interface
|   |-- AbsFFTJetAdjuster.h
|   |-- AbsFFTJetScaleCalculator.h
|   |-- AbsFFTSpecificScaleCalculator.h
|   |-- FFTGenericScaleCalculator.h
|   |-- FFTJet.h
|   |-- FFTJetAdjusters.h
|   |-- FFTJetCorrectionsTypemap.h
|   |-- FFTJetCorrector.h
|   |-- FFTJetCorrectorApp.h
|   |-- FFTJetCorrectorParametersLoader.h
|   |-- FFTJetCorrectorResult.h
|   |-- FFTJetCorrectorResultFromTransient.h
|   |-- FFTJetCorrectorSequence.h
|   |-- FFTJetCorrectorSequenceLoader.h
|   |-- FFTJetCorrectorSequenceRcd.h
|   |-- FFTJetCorrectorSequenceRcdTypes.h
|   |-- FFTJetCorrectorSequenceTypemap.h
|   |-- FFTJetCorrectorSequenceTypes.h
|   |-- FFTJetCorrectorTransient.h
|   |-- FFTJetCorrectorTransientFromJet.h
|   |-- FFTJetDict.h
|   |-- FFTJetLookupTableRcd.h
|   |-- FFTJetLookupTableRcdTypes.h
|   |-- FFTJetLookupTableSequence.h
|   |-- FFTJetLookupTableSequenceLoader.h
|   |-- FFTJetObjectFactory.h
|   |-- FFTJetRcdMapper.h
|   |-- FFTJetScaleCalculators.h
|   |-- L2AbsScaleCalculator.h
|   |-- L2RecoScaleCalculator.h
|   |-- L2ResScaleCalculator.h
|   `-- loadFFTJetInterpolationTable.h
`-- src
    |-- AbsFFTSpecificScaleCalculator.cc
    |-- FFTGenericScaleCalculator.cc
    |-- FFTJetCorrectorApp.cc
    |-- FFTJetCorrectorParametersLoader.cc
    |-- FFTJetCorrectorSequenceLoader.cc
    |-- FFTJetCorrectorSequenceRcdTypes.cc
    |-- FFTJetCorrectorSequenceTypes.cc
    |-- FFTJetLookupTableRcdTypes.cc
    |-- FFTJetLookupTableSequenceLoader.cc
    |-- T_EventSetup_LookupTable.cc
    `-- loadFFTJetInterpolationTable.cc
```

| File | Description |
| --- | --- |
| `BuildFile.xml` | Build rules for FFTJet correction objects and EventSetup loaders. |
| `interface/FFTJet.h` | Core FFTJet object definitions. This is the base physics object abstraction for FFTJet correction workflows. |
| `interface/FFTJetCorrector.h` | Main FFTJet corrector interface. It represents the correction operation applied to FFTJet-style jets. |
| `interface/FFTJetCorrectorApp.h` | Application-level helper for applying FFTJet corrector sequences. |
| `src/FFTJetCorrectorApp.cc` | Implements sequence application logic for FFTJet corrections. |
| `interface/FFTJetCorrectorResult.h` | Persistent result object for FFTJet correction output. |
| `interface/FFTJetCorrectorResultFromTransient.h` | Converter from transient correction output to persistent result form. |
| `interface/FFTJetCorrectorTransient.h` | Transient, in-memory FFTJet correction representation used during event processing. |
| `interface/FFTJetCorrectorTransientFromJet.h` | Converter from reco jets to transient FFTJet correction inputs. |
| `interface/FFTJetCorrectorSequence.h` | Container for ordered FFTJet correctors. Analogous in spirit to a chained JEC sequence. |
| `interface/FFTJetCorrectorSequenceLoader.h` | Loader for FFTJet correction sequences from EventSetup/conditions data. |
| `src/FFTJetCorrectorSequenceLoader.cc` | Implements FFTJet corrector sequence loading. |
| `interface/FFTJetCorrectorSequenceTypes.h` | Type definitions for supported FFTJet correction sequence categories. |
| `src/FFTJetCorrectorSequenceTypes.cc` | Implements/instantiates FFTJet sequence type metadata. |
| `interface/FFTJetCorrectorSequenceRcd.h` | EventSetup record wrapper for FFTJet corrector sequences. |
| `interface/FFTJetCorrectorSequenceRcdTypes.h` | Record type definitions for FFTJet corrector sequence payloads. |
| `src/FFTJetCorrectorSequenceRcdTypes.cc` | Registers/implements FFTJet sequence record type metadata. |
| `interface/FFTJetCorrectorSequenceTypemap.h` | Compile-time mapping between FFTJet sequence categories and record/payload types. |
| `interface/FFTJetCorrectorParametersLoader.h` | Loader for FFTJet corrector parameters from conditions payloads. |
| `src/FFTJetCorrectorParametersLoader.cc` | Implements FFTJet corrector parameter loading. |
| `interface/FFTJetLookupTableRcd.h` | EventSetup record wrapper for FFTJet lookup tables. |
| `interface/FFTJetLookupTableRcdTypes.h` | Record type definitions for FFTJet lookup table payloads. |
| `src/FFTJetLookupTableRcdTypes.cc` | Implements/instantiates FFTJet lookup table record metadata. |
| `interface/FFTJetLookupTableSequence.h` | Container for sequences of FFTJet lookup tables. |
| `interface/FFTJetLookupTableSequenceLoader.h` | Loader for lookup table sequences. |
| `src/FFTJetLookupTableSequenceLoader.cc` | Implements lookup table sequence loading. |
| `src/T_EventSetup_LookupTable.cc` | EventSetup type registration for lookup tables. |
| `interface/FFTJetObjectFactory.h` | Factory utilities for constructing FFTJet correction objects from type metadata. |
| `interface/FFTJetRcdMapper.h` | Maps FFTJet payload types to EventSetup records. |
| `interface/FFTJetCorrectionsTypemap.h` | Type mapping utilities for FFTJet correction payload categories. |
| `interface/FFTJetDict.h` | ROOT dictionary declarations for FFTJet objects. |
| `interface/loadFFTJetInterpolationTable.h` | Interface for loading FFTJet interpolation tables from stored forms. |
| `src/loadFFTJetInterpolationTable.cc` | Implements FFTJet interpolation table loading. |
| `interface/AbsFFTJetAdjuster.h` | Abstract interface for adjusting FFTJet quantities after correction. |
| `interface/FFTJetAdjusters.h` | Concrete adjuster templates/helpers for FFTJet corrected objects. |
| `interface/AbsFFTJetScaleCalculator.h` | Abstract interface for FFTJet scale calculators. |
| `interface/AbsFFTSpecificScaleCalculator.h` | Base class for scale calculators tied to specific FFTJet variables. |
| `src/AbsFFTSpecificScaleCalculator.cc` | Implements common behavior for specific FFTJet scale calculators. |
| `interface/FFTGenericScaleCalculator.h` | Generic FFTJet scale calculator interface/implementation. |
| `src/FFTGenericScaleCalculator.cc` | Implements generic scale calculation behavior. |
| `interface/FFTJetScaleCalculators.h` | Collection of FFTJet scale calculator types. |
| `interface/L2AbsScaleCalculator.h` | L2 absolute scale calculator for FFTJet correction workflows. |
| `interface/L2RecoScaleCalculator.h` | L2 reconstructed-scale calculator for FFTJet correction workflows. |
| `interface/L2ResScaleCalculator.h` | L2 residual scale calculator for FFTJet correction workflows. |

## FFTJetModules

Tree:

```text
FFTJetModules
|-- interface
|   `-- FFTJetESParameterParser.h
|-- plugins
|   |-- BuildFile.xml
|   |-- FFTJetCorrectionESProducer.h
|   |-- FFTJetCorrectionESProducer_0.cc
|   |-- FFTJetCorrectionESProducer_1.cc
|   |-- FFTJetCorrectionESProducer_2.cc
|   |-- FFTJetCorrectionESProducer_3.cc
|   |-- FFTJetCorrectionESProducer_4.cc
|   |-- FFTJetCorrectionESProducer_5.cc
|   |-- FFTJetCorrectionESProducer_6.cc
|   |-- FFTJetCorrectorDBReader.cc
|   |-- FFTJetCorrectorDBWriter.cc
|   |-- FFTJetLookupTableESProducer.cc
|   `-- FFTJetSealModule.cc
|-- python
|   |-- fftjetcorrectionesproducer_cfi.py
|   `-- fftjetlookuptableesproducer_cfi.py
`-- test
    |-- FFTJetCorrectorDBReader_cfg.py
    |-- FFTJetCorrectorDBWriter_cfg.py
    `-- fftjet_corr.gssa
```

| File | Description |
| --- | --- |
| `interface/FFTJetESParameterParser.h` | Helper for parsing FFTJet ESProducer parameters. It keeps the many FFTJet record/type labels consistent. |
| `plugins/FFTJetCorrectionESProducer.h` | Template ESProducer for serving FFTJet correction sequences from EventSetup. |
| `plugins/FFTJetCorrectionESProducer_0.cc` | Registers one concrete FFTJet correction ESProducer type. |
| `plugins/FFTJetCorrectionESProducer_1.cc` | Registers one concrete FFTJet correction ESProducer type. |
| `plugins/FFTJetCorrectionESProducer_2.cc` | Registers one concrete FFTJet correction ESProducer type. |
| `plugins/FFTJetCorrectionESProducer_3.cc` | Registers one concrete FFTJet correction ESProducer type. |
| `plugins/FFTJetCorrectionESProducer_4.cc` | Registers one concrete FFTJet correction ESProducer type. |
| `plugins/FFTJetCorrectionESProducer_5.cc` | Registers one concrete FFTJet correction ESProducer type. |
| `plugins/FFTJetCorrectionESProducer_6.cc` | Registers one concrete FFTJet correction ESProducer type. |
| `plugins/FFTJetLookupTableESProducer.cc` | ESProducer for serving FFTJet lookup table sequences. |
| `plugins/FFTJetCorrectorDBWriter.cc` | Analyzer/module for writing FFTJet correction payloads to a DB. |
| `plugins/FFTJetCorrectorDBReader.cc` | Analyzer/module for reading FFTJet correction payloads from a DB. |
| `plugins/FFTJetSealModule.cc` | Plugin registration glue for FFTJet modules. |
| `plugins/BuildFile.xml` | Build rules for FFTJet plugins. |
| `python/fftjetcorrectionesproducer_cfi.py` | Python factory/config mapping FFTJet correction types to ESProducer labels and records. |
| `python/fftjetlookuptableesproducer_cfi.py` | Python factory/config mapping FFTJet lookup table types to ESProducer labels and records. |
| `test/FFTJetCorrectorDBWriter_cfg.py` | Test configuration for writing FFTJet correction payloads. |
| `test/FFTJetCorrectorDBReader_cfg.py` | Test configuration for reading FFTJet correction payloads. |
| `test/fftjet_corr.gssa` | Serialized/test FFTJet correction input data used by the DB tests. |

## InterpolationTables

Tree:

```text
InterpolationTables
|-- BuildFile.xml
|-- interface
|   |-- AbsArrayProjector.h
|   |-- AbsMultivariateFunctor.h
|   |-- AbsVisitor.h
|   |-- ArrayND.h
|   |-- ArrayNDScanner.h
|   |-- ArrayRange.h
|   |-- ArrayShape.h
|   |-- BoxND.h
|   |-- CircularMapper1d.h
|   |-- ComplexComparesAbs.h
|   |-- ComplexComparesFalse.h
|   |-- CoordinateSelector.h
|   |-- DualAxis.h
|   |-- DualHistoAxis.h
|   |-- EquidistantSequence.h
|   |-- GridAxis.h
|   |-- HistoAxis.h
|   |-- HistoND.h
|   |-- HistoNDFunctorInstances.h
|   |-- InterpolationFunctorInstances.h
|   |-- Interval.h
|   |-- LinInterpolatedTableND.h
|   |-- LinearMapper1d.h
|   |-- NUHistoAxis.h
|   |-- NpstatException.h
|   |-- PreciseType.h
|   |-- ProperDblFromCmpl.h
|   |-- SimpleFunctors.h
|   |-- StorableHistoNDFunctor.h
|   |-- StorableInterpolationFunctor.h
|   |-- StorableMultivariateFunctor.h
|   |-- StorableMultivariateFunctorReader.h
|   |-- UniformAxis.h
|   |-- absDifference.h
|   |-- allocators.h
|   |-- closeWithinTolerance.h
|   |-- convertAxis.h
|   |-- interpolate.h
|   |-- interpolateHistoND.h
|   `-- isMonotonous.h
|-- src
|   |-- ArrayNDScanner.cc
|   |-- ArrayRange.cc
|   |-- ArrayShape.cc
|   |-- DualAxis.cc
|   |-- DualHistoAxis.cc
|   |-- EquidistantSequence.cc
|   |-- GridAxis.cc
|   |-- HistoAxis.cc
|   |-- NUHistoAxis.cc
|   |-- StorableMultivariateFunctor.cc
|   |-- StorableMultivariateFunctorReader.cc
|   |-- UniformAxis.cc
|   `-- convertAxis.cc
`-- test
    `-- port_npstat_to_cmssw.tcl
```

| File | Description |
| --- | --- |
| `BuildFile.xml` | Build rules for the generic interpolation library. |
| `interface/AbsMultivariateFunctor.h` | Abstract interface for a function of multiple variables. Correction tables use this pattern to evaluate payload-dependent quantities. |
| `interface/StorableMultivariateFunctor.h` | Persistable multivariate functor interface. It allows interpolation functions to be stored in payloads. |
| `src/StorableMultivariateFunctor.cc` | Implements common persistable functor behavior. |
| `interface/StorableMultivariateFunctorReader.h` | Reader helper for stored functor objects. |
| `src/StorableMultivariateFunctorReader.cc` | Implements stored functor reading. |
| `interface/StorableInterpolationFunctor.h` | Storable interpolation functor abstraction. Used when correction information is represented as interpolated tables. |
| `interface/StorableHistoNDFunctor.h` | Storable histogram-backed functor abstraction. |
| `interface/LinInterpolatedTableND.h` | N-dimensional linear interpolation table. This is the key numerical tool for table-based corrections. |
| `interface/interpolate.h` | Generic interpolation helper functions. |
| `interface/interpolateHistoND.h` | Interpolation helpers specialized for N-dimensional histograms. |
| `interface/InterpolationFunctorInstances.h` | Template instantiation declarations for interpolation functors. |
| `interface/HistoNDFunctorInstances.h` | Template instantiation declarations for histogram-backed functors. |
| `interface/HistoND.h` | Large N-dimensional histogram template. It provides binning, storage, arithmetic, and projection functionality. |
| `interface/HistoAxis.h` | Histogram axis representation with bin edges and coordinate mapping. |
| `src/HistoAxis.cc` | Implements histogram axis behavior. |
| `interface/NUHistoAxis.h` | Non-uniform histogram axis representation. |
| `src/NUHistoAxis.cc` | Implements non-uniform histogram axis behavior. |
| `interface/UniformAxis.h` | Uniform axis representation. |
| `src/UniformAxis.cc` | Implements uniform axis behavior. |
| `interface/GridAxis.h` | Grid axis helper for table coordinates. |
| `src/GridAxis.cc` | Implements grid axis operations. |
| `interface/DualAxis.h` | Axis helper that supports dual coordinate/bin interpretations. |
| `src/DualAxis.cc` | Implements dual-axis behavior. |
| `interface/DualHistoAxis.h` | Histogram-axis variant of the dual-axis helper. |
| `src/DualHistoAxis.cc` | Implements dual histogram-axis behavior. |
| `interface/EquidistantSequence.h` | Helper for equidistant bin/coordinate sequences. |
| `src/EquidistantSequence.cc` | Implements equidistant sequence operations. |
| `interface/LinearMapper1d.h` | One-dimensional linear mapping helper. |
| `interface/CircularMapper1d.h` | One-dimensional circular mapping helper, useful for angular variables. |
| `interface/ArrayND.h` | Generic multidimensional array template. This is the storage backbone for many table and histogram classes. |
| `interface/ArrayNDScanner.h` | Iterator/scanner over N-dimensional arrays. |
| `src/ArrayNDScanner.cc` | Implements scanner behavior. |
| `interface/ArrayRange.h` | Represents a range/slice of an array. |
| `src/ArrayRange.cc` | Implements array-range operations. |
| `interface/ArrayShape.h` | Stores dimensions and strides of N-dimensional arrays. |
| `src/ArrayShape.cc` | Implements array-shape operations. |
| `interface/BoxND.h` | N-dimensional box/range helper. |
| `interface/CoordinateSelector.h` | Helper for selecting coordinates from multidimensional inputs. |
| `interface/AbsArrayProjector.h` | Abstract interface for projecting arrays/histograms to lower dimensions. |
| `interface/AbsVisitor.h` | Visitor interface used by table/functor objects. |
| `interface/SimpleFunctors.h` | Small generic functor utilities. |
| `interface/Interval.h` | Interval helper for numerical ranges. |
| `interface/PreciseType.h` | Type trait selecting a precise arithmetic type. |
| `interface/ProperDblFromCmpl.h` | Type trait for deriving real-valued doubles from complex-valued templates. |
| `interface/ComplexComparesAbs.h` | Comparator for complex numbers using absolute value. |
| `interface/ComplexComparesFalse.h` | Comparator stub for complex types where ordering is intentionally disabled. |
| `interface/absDifference.h` | Helper computing absolute differences in a type-aware way. |
| `interface/closeWithinTolerance.h` | Numerical tolerance comparison helper. |
| `interface/isMonotonous.h` | Monotonicity-check helper for axes/sequences. |
| `interface/allocators.h` | Allocator utilities for table containers. |
| `interface/NpstatException.h` | Exception type used by the interpolation/table code. |
| `interface/convertAxis.h` | Interface for converting between axis representations. |
| `src/convertAxis.cc` | Implements axis conversion logic. |
| `test/port_npstat_to_cmssw.tcl` | Porting helper script from the original npstat-style code into CMSSW layout. |

## TauJet

Tree:

```text
TauJet
|-- BuildFile.xml
|-- data
|   |-- IterativeCone0.4_EtScheme_TowerEt0.5_E0.8_Jets871_2x1033PU_tau.txt
|   |-- IterativeCone0.4_standardCMSSW_120_tau.txt
|   `-- IterativeCone0.5_standardCMSSW_16x_tau.txt
|-- plugins
|   |-- BuildFile.xml
|   `-- TauJetCorrectorExample.cc
`-- python
    |-- TauJetAlgoParameters_cfi.py
    `-- TauJetCorrections_cff.py
```

| File | Description |
| --- | --- |
| `BuildFile.xml` | Build rules for the legacy tau-jet correction package. |
| `python/TauJetAlgoParameters_cfi.py` | Parameter set for tau-jet correction examples, including source jet collection and trigger type. |
| `python/TauJetCorrections_cff.py` | Legacy tau-jet correction sequence using an ORCA-derived correction service and a jet correction producer. |
| `plugins/TauJetCorrectorExample.cc` | Example plugin demonstrating tau-jet correction usage. |
| `plugins/BuildFile.xml` | Build rules for the tau-jet plugin. |
| `data/IterativeCone0.4_standardCMSSW_120_tau.txt` | Legacy tau-jet correction table for iterative-cone 0.4 jets in an old CMSSW setup. |
| `data/IterativeCone0.5_standardCMSSW_16x_tau.txt` | Legacy tau-jet correction table for iterative-cone 0.5 jets. |
| `data/IterativeCone0.4_EtScheme_TowerEt0.5_E0.8_Jets871_2x1033PU_tau.txt` | Legacy tau-jet correction table for a specific tower/Et-scheme pileup scenario. |

## JetVertexAssociation

Tree:

```text
JetVertexAssociation
|-- BuildFile.xml
|-- interface
|   |-- JetVertexAssociation.h
|   `-- JetVertexMain.h
|-- src
|   |-- JetVertexAssociation.cc
|   |-- JetVertexMain.cc
|   `-- SealModule.cc
`-- test
    |-- AnalysisJV.cc
    |-- AnalysisJV.h
    `-- BuildFile.xml
```

| File | Description |
| --- | --- |
| `BuildFile.xml` | Build rules for the jet-vertex association package. |
| `interface/JetVertexAssociation.h` | Interface for associating jets to vertices. This is a legacy pileup/vertex-discrimination helper. |
| `src/JetVertexAssociation.cc` | Implements jet-vertex association logic. |
| `interface/JetVertexMain.h` | Main producer/analyzer interface for the jet-vertex workflow. |
| `src/JetVertexMain.cc` | Implements the main jet-vertex module behavior. |
| `src/SealModule.cc` | Registers jet-vertex association plugins. |
| `test/AnalysisJV.h` | Test analyzer interface for reading jet-vertex association outputs. |
| `test/AnalysisJV.cc` | Test analyzer implementation that inspects association variables and jet collections. |
| `test/BuildFile.xml` | Build rules for the jet-vertex association test analyzer. |

## MinBias

Tree:

```text
MinBias
|-- BuildFile.xml
|-- interface
|   `-- MinBias.h
|-- src
|   |-- MinBias.cc
|   `-- SealModule.cc
`-- test
    |-- MinBias.C
    |-- MinBias.h
    |-- PoolFileCatalog.xml.BAK
    `-- rootlogon.C.old
```

| File | Description |
| --- | --- |
| `BuildFile.xml` | Build rules for the legacy min-bias package. |
| `interface/MinBias.h` | Interface for the min-bias correction/validation module. |
| `src/MinBias.cc` | Implements legacy min-bias event handling used in old correction studies. |
| `src/SealModule.cc` | Registers the min-bias plugin. |
| `test/MinBias.C` | ROOT macro implementation for reading/plotting min-bias trees. |
| `test/MinBias.h` | ROOT-generated tree reader header for min-bias validation. |
| `test/PoolFileCatalog.xml.BAK` | Backup pool catalog for old local tests. Historical artifact. |
| `test/rootlogon.C.old` | Old ROOT startup macro for min-bias tests. Historical artifact. |

## IsolatedParticles

Tree:

```text
IsolatedParticles
`-- test
    |-- BuildFile.xml
    |-- IsoHists.root
    |-- TestIsoSimTracks.cc
    `-- TestIsoTracks.cc
```

| File | Description |
| --- | --- |
| `test/TestIsoTracks.cc` | Test analyzer/source for isolated reconstructed-track studies. It is related to validation of single-particle or isolated-track response. |
| `test/TestIsoSimTracks.cc` | Test analyzer/source for isolated simulated-track studies. Useful for MC truth comparison in isolated-particle validation. |
| `test/IsoHists.root` | ROOT histogram file used by the isolated-particle tests. This is binary test/reference data rather than source code. |
| `test/BuildFile.xml` | Build rules for isolated-particle test code. |

