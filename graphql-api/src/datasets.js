const DATASET_LABELS = {
  gnomad_r3: 'gnomAD v3',
  gnomad_r3_controls_and_biobanks: 'gnomAD v3 (controls and biobanks)',
  gnomad_r3_hgdp: 'gnomAD v3 (HGDP)',
  gnomad_r3_non_cancer: 'gnomAD v3 (non-cancer)',
  gnomad_r3_non_neuro: 'gnomAD v3 (non-neuro)',
  gnomad_r3_non_topmed: 'gnomAD v3 (non-TOPMed)',
  gnomad_r3_non_v2: 'gnomAD v3 (non-v2)',
  gnomad_r3_tgp: 'gnomAD v3 (TGP)',
  gnomad_r2_1: 'gnomAD v2',
  gnomad_r2_1_controls: 'gnomAD v2 (controls)',
  gnomad_r2_1_non_neuro: 'gnomAD v2 (non-neuro)',
  gnomad_r2_1_non_cancer: 'gnomAD v2 (non-cancer)',
  gnomad_r2_1_non_topmed: 'gnomAD v2 (non-TOPMed)',
  exac: 'ExAC',
}

const DATASET_REFERENCE_GENOMES = {
  gnomad_r3: 'GRCh38',
  gnomad_r3_controls_and_biobanks: 'GRCh38',
  gnomad_r3_hgdp: 'GRCh38',
  gnomad_r3_non_cancer: 'GRCh38',
  gnomad_r3_non_neuro: 'GRCh38',
  gnomad_r3_non_topmed: 'GRCh38',
  gnomad_r3_non_v2: 'GRCh38',
  gnomad_r3_tgp: 'GRCh38',
  gnomad_r2_1: 'GRCh37',
  gnomad_r2_1_controls: 'GRCh37',
  gnomad_r2_1_non_neuro: 'GRCh37',
  gnomad_r2_1_non_cancer: 'GRCh37',
  gnomad_r2_1_non_topmed: 'GRCh37',
  exac: 'GRCh37',
}

module.exports = {
  DATASET_LABELS,
  DATASET_REFERENCE_GENOMES,
}
