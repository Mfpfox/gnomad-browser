import hail as hl


def normalized_contig(contig: hl.expr.StringExpression) -> hl.expr.StringExpression:
    return contig.replace("^chr", "")


def contig_number(contig: hl.expr.StringExpression) -> hl.expr.Int32Expression:
    return hl.bind(
        lambda contig: (
            hl.case().when(contig == "X", 23).when(contig == "Y", 24).when(contig[0] == "M", 25).default(hl.int(contig))
        ),
        normalized_contig(contig),
    )


def x_position(locus: hl.expr.LocusExpression) -> hl.expr.Int64Expression:
    return hl.int64(contig_number(locus.contig)) * 1_000_000_000 + locus.position
