import hail as hl

from data_pipeline.variants.transcript_consequences.hgvs import hgvsp_from_consequence_amino_acids
from data_pipeline.variants.transcript_consequences.vep import consequence_term_rank


OMIT_CONSEQUENCE_TERMS = hl.set(["upstream_gene_variant", "downstream_gene_variant"])


def annotate_transcript_consequences(variants_path, transcript_models_path, mane_transcripts_path=None):
    ds = hl.read_table(variants_path)

    most_severe_consequence = ds.vep.most_severe_consequence

    transcript_consequences = ds.vep.transcript_consequences

    # Drop irrelevant consequences
    transcript_consequences = transcript_consequences.map(
        lambda c: c.annotate(
            consequence_terms=c.consequence_terms.filter(lambda t: ~OMIT_CONSEQUENCE_TERMS.contains(t))
        )
    ).filter(lambda c: c.consequence_terms.size() > 0)

    # Add/transmute derived fields
    transcript_consequences = transcript_consequences.map(
        lambda c: c.annotate(major_consequence=hl.sorted(c.consequence_terms, key=consequence_term_rank)[0])
    ).map(
        lambda c: c.annotate(
            domains=c.domains.map(lambda domain: domain.db + ":" + domain.name),
            hgvsc=c.hgvsc.split(":")[-1],
            hgvsp=hgvsp_from_consequence_amino_acids(c),
            is_canonical=hl.bool(c.canonical),
        )
    )

    transcript_consequences = transcript_consequences.map(
        lambda c: c.select(
            "biotype",
            "consequence_terms",
            "domains",
            "gene_id",
            "gene_symbol",
            "hgvsc",
            "hgvsp",
            "is_canonical",
            "lof_filter",
            "lof_flags",
            "lof",
            "major_consequence",
            "polyphen_prediction",
            "sift_prediction",
            "transcript_id",
        )
    )

    transcripts = hl.read_table(transcript_models_path)

    transcript_info = hl.dict(
        [
            (row.transcript_id, row.transcript_info)
            for row in transcripts.select(
                transcript_info=hl.struct(
                    transcript_version=transcripts.transcript_version, gene_version=transcripts.gene.gene_version,
                )
            ).collect()
        ]
    )

    transcript_consequences = transcript_consequences.map(
        lambda csq: csq.annotate(**transcript_info.get(csq.transcript_id))
    )

    if mane_transcripts_path:
        mane_transcripts = hl.read_table(mane_transcripts_path)

        mane_transcripts = hl.dict([(row.gene_id, row.drop("gene_id")) for row in mane_transcripts.collect()])

        transcript_consequences = transcript_consequences.map(
            lambda csq: csq.annotate(
                **hl.rbind(
                    mane_transcripts.get(csq.gene_id),
                    lambda mane_transcript: (
                        hl.case()
                        .when(
                            (mane_transcript.ensembl_id == csq.transcript_id)
                            & (mane_transcript.ensembl_version == csq.transcript_version),
                            hl.struct(
                                is_mane_select=True,
                                is_mane_select_version=True,
                                refseq_id=mane_transcript.refseq_id,
                                refseq_version=mane_transcript.refseq_version,
                            ),
                        )
                        .when(
                            mane_transcript.ensembl_id == csq.transcript_id,
                            hl.struct(
                                is_mane_select=True,
                                is_mane_select_version=False,
                                refseq_id=hl.null(hl.tstr),
                                refseq_version=hl.null(hl.tstr),
                            ),
                        )
                        .default(
                            hl.struct(
                                is_mane_select=False,
                                is_mane_select_version=False,
                                refseq_id=hl.null(hl.tstr),
                                refseq_version=hl.null(hl.tstr),
                            )
                        )
                    ),
                )
            )
        )

        transcript_consequences = hl.sorted(
            transcript_consequences,
            lambda c: (
                hl.if_else(c.biotype == "protein_coding", 0, 1, missing_false=True),
                hl.if_else(c.major_consequence == most_severe_consequence, 0, 1, missing_false=True),
                hl.if_else(c.is_mane_select, 0, 1, missing_false=True),
                hl.if_else(c.is_canonical, 0, 1, missing_false=True),
            ),
        )

    else:
        transcript_consequences = hl.sorted(
            transcript_consequences,
            lambda c: (
                hl.if_else(c.biotype == "protein_coding", 0, 1, missing_false=True),
                hl.if_else(c.major_consequence == most_severe_consequence, 0, 1, missing_false=True),
                hl.if_else(c.is_canonical, 0, 1, missing_false=True),
            ),
        )

    ds = ds.annotate(transcript_consequences=transcript_consequences).drop("vep")

    return ds
