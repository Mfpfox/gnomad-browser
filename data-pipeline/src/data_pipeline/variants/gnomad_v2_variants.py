import hail as hl

from data_pipeline.position_fields import normalized_contig, x_position
from data_pipeline.variants.variant_id import variant_id


POPULATIONS = ["afr", "amr", "asj", "eas", "fin", "nfe", "oth", "sas"]

SUBPOPULATIONS = {
    "eas": ["jpn", "kor", "oea"],
    "nfe": ["bgr", "est", "nwe", "onf", "seu", "swe"],
}


def population_frequencies_expression(ds, freq_index_dict, subset):
    populations = []

    for pop_id in POPULATIONS:
        # Genomes do not have SAS data
        if f"{subset}_{pop_id}" not in freq_index_dict:
            # TODO: Remove these if populations table can handle their absence
            populations.append(hl.struct(id=pop_id.upper(), ac=0, an=0, hemizygote_count=0, homozygote_count=0))
            populations.append(
                hl.struct(id=f"{pop_id.upper()}_FEMALE", ac=0, an=0, hemizygote_count=0, homozygote_count=0)
            )
            populations.append(
                hl.struct(id=f"{pop_id.upper()}_MALE", ac=0, an=0, hemizygote_count=0, homozygote_count=0)
            )

            continue

        populations.append(
            hl.struct(
                id=pop_id.upper(),
                ac=ds.freq[freq_index_dict[f"{subset}_{pop_id}"]].AC,
                an=ds.freq[freq_index_dict[f"{subset}_{pop_id}"]].AN,
                hemizygote_count=hl.if_else(ds.nonpar, ds.freq[freq_index_dict[f"{subset}_{pop_id}_male"]].AN, 0),
                homozygote_count=ds.freq[freq_index_dict[f"{subset}_{pop_id}"]].homozygote_count,
            )
        )

        for sub_pop_id in SUBPOPULATIONS.get(pop_id, []):
            # Genomes do not have EAS sub-population data
            if f"{subset}_{pop_id}_{sub_pop_id}" not in freq_index_dict:
                # TODO: Remove this if populations table can handle its absence
                populations.append(
                    hl.struct(
                        id=f"{pop_id.upper()}_{sub_pop_id.upper()}",
                        ac=0,
                        an=0,
                        hemizygote_count=hl.null(hl.tint),
                        homozygote_count=0,
                    )
                )

                continue

            populations.append(
                hl.struct(
                    id=f"{pop_id.upper()}_{sub_pop_id.upper()}",
                    ac=ds.freq[freq_index_dict[f"{subset}_{pop_id}_{sub_pop_id}"]].AC,
                    an=ds.freq[freq_index_dict[f"{subset}_{pop_id}_{sub_pop_id}"]].AN,
                    hemizygote_count=hl.null(hl.tint),
                    homozygote_count=ds.freq[freq_index_dict[f"{subset}_{pop_id}_{sub_pop_id}"]].homozygote_count,
                )
            )

        populations.append(
            hl.struct(
                id=f"{pop_id.upper()}_FEMALE",
                ac=ds.freq[freq_index_dict[f"{subset}_{pop_id}_female"]].AC,
                an=ds.freq[freq_index_dict[f"{subset}_{pop_id}_female"]].AN,
                hemizygote_count=0,
                homozygote_count=ds.freq[freq_index_dict[f"{subset}_{pop_id}_female"]].homozygote_count,
            )
        )

        populations.append(
            hl.struct(
                id=f"{pop_id.upper()}_MALE",
                ac=ds.freq[freq_index_dict[f"{subset}_{pop_id}_male"]].AC,
                an=ds.freq[freq_index_dict[f"{subset}_{pop_id}_male"]].AN,
                hemizygote_count=hl.if_else(ds.nonpar, ds.freq[freq_index_dict[f"{subset}_{pop_id}_male"]].AC, 0),
                homozygote_count=ds.freq[freq_index_dict[f"{subset}_{pop_id}_male"]].homozygote_count,
            )
        )

    populations.append(
        hl.struct(
            id="FEMALE",
            ac=ds.freq[freq_index_dict[f"{subset}_female"]].AC,
            an=ds.freq[freq_index_dict[f"{subset}_female"]].AN,
            hemizygote_count=0,
            homozygote_count=ds.freq[freq_index_dict[f"{subset}_female"]].homozygote_count,
        )
    )

    populations.append(
        hl.struct(
            id="MALE",
            ac=ds.freq[freq_index_dict[f"{subset}_male"]].AC,
            an=ds.freq[freq_index_dict[f"{subset}_male"]].AN,
            hemizygote_count=hl.if_else(ds.nonpar, ds.freq[freq_index_dict[f"{subset}_male"]].AC, 0),
            homozygote_count=ds.freq[freq_index_dict[f"{subset}_male"]].homozygote_count,
        )
    )

    return populations


def prepare_gnomad_v2_variants_helper(path, exome_or_genome):
    ds = hl.read_table(path)

    ###############
    # Frequencies #
    ###############

    g = hl.eval(ds.globals)

    ds = ds.select_globals()

    ds = ds.annotate(
        freq=hl.struct(
            **{
                subset: hl.struct(
                    ac=ds.freq[g.freq_index_dict[subset]].AC,
                    ac_raw=ds.freq[g.freq_index_dict[f"{subset}_raw"]].AC,
                    an=ds.freq[g.freq_index_dict[subset]].AN,
                    hemizygote_count=hl.if_else(ds.nonpar, ds.freq[g.freq_index_dict[f"{subset}_male"]].AC, 0),
                    homozygote_count=ds.freq[g.freq_index_dict[subset]].homozygote_count,
                    populations=population_frequencies_expression(ds, g.freq_index_dict, subset),
                )
                for subset in (
                    ["gnomad", "controls", "non_neuro", "non_topmed"]
                    + (["non_cancer"] if exome_or_genome == "exome" else [])
                )
            }
        )
    )

    ##############################
    # Filtering allele frequency #
    ##############################

    ds = ds.annotate(
        freq=ds.freq.annotate(
            **{
                subset: ds.freq[subset].annotate(
                    faf95=hl.rbind(
                        hl.sorted(
                            hl.array(
                                [
                                    hl.struct(
                                        faf=ds.faf[g.faf_index_dict[f"{subset}_{pop_id}"]].faf95,
                                        population=pop_id.upper(),
                                    )
                                    for pop_id in (
                                        ["afr", "amr", "eas", "nfe"] + (["sas"] if exome_or_genome == "exome" else [])
                                    )
                                ]
                            ).filter(lambda f: f.faf > 0),
                            key=lambda f: (-f.faf, f.population),
                        ),
                        lambda fafs: hl.if_else(
                            hl.len(fafs) > 0,
                            hl.struct(popmax=fafs[0].faf, popmax_population=fafs[0].population,),
                            hl.struct(popmax=hl.null(hl.tfloat), popmax_population=hl.null(hl.tstr),),
                        ),
                    ),
                    faf99=hl.rbind(
                        hl.sorted(
                            hl.array(
                                [
                                    hl.struct(
                                        faf=ds.faf[g.faf_index_dict[f"{subset}_{pop_id}"]].faf99,
                                        population=pop_id.upper(),
                                    )
                                    for pop_id in (
                                        ["afr", "amr", "eas", "nfe"] + (["sas"] if exome_or_genome == "exome" else [])
                                    )
                                ]
                            ).filter(lambda f: f.faf > 0),
                            key=lambda f: (-f.faf, f.population),
                        ),
                        lambda fafs: hl.if_else(
                            hl.len(fafs) > 0,
                            hl.struct(popmax=fafs[0].faf, popmax_population=fafs[0].population,),
                            hl.struct(popmax=hl.null(hl.tfloat), popmax_population=hl.null(hl.tstr),),
                        ),
                    ),
                )
                for subset in (
                    ["gnomad", "controls", "non_neuro", "non_topmed"]
                    + (["non_cancer"] if exome_or_genome == "exome" else [])
                )
            }
        ),
    )

    ds = ds.drop("faf")

    ####################
    # Age distribution #
    ####################

    # Extract overall age distribution
    ds = ds.transmute(
        age_distribution=hl.struct(
            het=ds.age_hist_het[g.age_index_dict["gnomad"]], hom=ds.age_hist_hom[g.age_index_dict["gnomad"]],
        )
    )

    ###################
    # Quality metrics #
    ###################

    ds = ds.transmute(
        quality_metrics=hl.struct(
            allele_balance=hl.struct(alt=ds.ab_hist_alt,),
            genotype_depth=hl.struct(all=ds.dp_hist_all, alt=ds.dp_hist_alt,),
            genotype_quality=hl.struct(all=ds.gq_hist_all, alt=ds.gq_hist_alt,),
            # Use the same fields as the VCFs
            # Based https://github.com/macarthur-lab/gnomad_qc/blob/25a81bc2166fbe4ccbb2f7a87d36aba661150413/variant_qc/prepare_data_release.py#L128-L159
            site_quality_metrics=[
                hl.struct(metric="BaseQRankSum", value=ds.allele_info.BaseQRankSum),
                hl.struct(metric="ClippingRankSum", value=ds.allele_info.ClippingRankSum),
                hl.struct(metric="DP", value=hl.float(ds.allele_info.DP)),
                hl.struct(metric="FS", value=ds.info_FS),
                hl.struct(metric="InbreedingCoeff", value=ds.info_InbreedingCoeff),
                hl.struct(metric="MQ", value=ds.info_MQ),
                hl.struct(metric="MQRankSum", value=ds.info_MQRankSum),
                hl.struct(metric="pab_max", value=ds.pab_max),
                hl.struct(metric="QD", value=ds.info_QD),
                hl.struct(metric="ReadPosRankSum", value=ds.info_ReadPosRankSum),
                hl.struct(metric="RF", value=ds.rf_probability),
                hl.struct(metric="SiteQuality", value=ds.qual),
                hl.struct(metric="SOR", value=ds.info_SOR),
                hl.struct(metric="VQSLOD", value=ds.allele_info.VQSLOD),
                hl.struct(metric="VQSR_NEGATIVE_TRAIN_SITE", value=hl.float(ds.info_NEGATIVE_TRAIN_SITE)),
                hl.struct(metric="VQSR_POSITIVE_TRAIN_SITE", value=hl.float(ds.info_POSITIVE_TRAIN_SITE)),
            ],
        )
    )

    #################
    # Unused fields #
    #################

    ds = ds.drop(
        "adj_biallelic_rank",
        "adj_biallelic_singleton_rank",
        "adj_rank",
        "adj_singleton_rank",
        "allele_type",
        "biallelic_rank",
        "biallelic_singleton_rank",
        "has_star",
        "info_DP",
        "mills",
        "n_alt_alleles",
        "n_nonref",
        "omni",
        "popmax",
        "qd",
        "rank",
        "score",
        "singleton_rank",
        "singleton",
        "transmitted_singleton",
        "variant_type",
        "was_mixed",
        "was_split",
    )

    # These two fields appear only in the genomes table
    if "_score" in ds.row_value.dtype.fields:
        ds = ds.drop("_score", "_singleton")

    ds = ds.select(**{exome_or_genome: ds.row_value})

    return ds


def prepare_gnomad_v2_variants(exome_variants_path, genome_variants_path):
    exome_variants = prepare_gnomad_v2_variants_helper(exome_variants_path, "exome")
    genome_variants = prepare_gnomad_v2_variants_helper(genome_variants_path, "genome")

    shared_fields = [
        "lcr",
        "nonpar",
        "rsid",
        "segdup",
        "vep",
    ]

    variants = exome_variants.join(genome_variants, "outer")

    variants = variants.annotate(
        **{field: hl.or_else(variants.exome[field], variants.genome[field]) for field in shared_fields}
    )

    variants = variants.annotate(exome=variants.exome.drop(*shared_fields), genome=variants.genome.drop(*shared_fields))

    variants = variants.annotate(
        variant_id=variant_id(variants.locus, variants.alleles),
        reference_genome="GRCh37",
        chrom=normalized_contig(variants.locus.contig),
        pos=variants.locus.position,
        xpos=x_position(variants.locus),
        ref=variants.alleles[0],
        alt=variants.alleles[1],
    )

    # Flags
    variants = variants.annotate(
        flags=hl.set(
            [
                hl.or_missing(variants.lcr, "lcr"),
                hl.or_missing(((variants.chrom == "X") | (variants.chrom == "Y")) & ~variants.nonpar, "par"),
            ]
        ).filter(hl.is_defined)
    )

    # Colocated variants
    variants = variants.cache()
    variants_by_locus = variants.select(
        variants.variant_id,
        exome_ac_raw=hl.struct(**{f: variants.exome.freq[f].ac_raw for f in variants.exome.freq.dtype.fields}),
        genome_ac_raw=hl.struct(
            non_cancer=variants.genome.freq.gnomad.ac_raw,
            **{f: variants.genome.freq[f].ac_raw for f in variants.genome.freq.dtype.fields},
        ),
    )
    variants_by_locus = variants_by_locus.group_by("locus").aggregate(
        variants=hl.agg.collect(variants_by_locus.row_value)
    )

    def subset_filter(subset):
        return lambda variant: (variant.exome_ac_raw[subset] > 0) | (variant.genome_ac_raw[subset] > 0)

    variants_by_locus = variants_by_locus.annotate(
        variant_ids=hl.struct(
            **{
                subset: variants_by_locus.variants.filter(subset_filter(subset)).map(lambda variant: variant.variant_id)
                for subset in ["gnomad", "controls", "non_cancer", "non_neuro", "non_topmed"]
            }
        )
    )

    variants = variants.annotate(colocated_variants=variants_by_locus[variants.locus].variant_ids)
    variants = variants.annotate(
        colocated_variants=hl.struct(
            **{
                subset: variants.colocated_variants[subset].filter(lambda variant_id: variant_id != variants.variant_id)
                for subset in ["gnomad", "controls", "non_cancer", "non_neuro", "non_topmed"]
            }
        )
    )

    return variants
