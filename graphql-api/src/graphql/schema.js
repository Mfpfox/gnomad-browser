const path = require('path')

const { loadFilesSync } = require('@graphql-tools/load-files')
const { mergeTypeDefs, mergeResolvers } = require('@graphql-tools/merge')
const { makeExecutableSchema } = require('@graphql-tools/schema')

const aliasResolvers = require('./resolvers/aliases')
const clinVarVariantResolvers = require('./resolvers/clinvar_variants')
const coverageResolvers = require('./resolvers/coverage')
const geneResolvers = require('./resolvers/gene')
const geneFieldResolvers = require('./resolvers/gene_fields')
const multiNucleotideVariantResolves = require('./resolvers/multi_nucleotide_variants')
const regionResolvers = require('./resolvers/region')
const regionFieldResolvers = require('./resolvers/region_fields')
const searchResolvers = require('./resolvers/search')
const structuralVariantResolvers = require('./resolvers/structural_variants')
const transcriptResolvers = require('./resolvers/transcript')
const transcriptFieldResolvers = require('./resolvers/transcript_fields')
const variantResolvers = require('./resolvers/variants')

const typeDefs = mergeTypeDefs([
  ...loadFilesSync(path.join(__dirname, './types')),
  'directive @cost(value: Int!, multipliers: [String!]) on FIELD_DEFINITION',
])

const resolvers = mergeResolvers([
  aliasResolvers,
  clinVarVariantResolvers,
  coverageResolvers,
  geneResolvers,
  geneFieldResolvers,
  multiNucleotideVariantResolves,
  regionResolvers,
  regionFieldResolvers,
  searchResolvers,
  structuralVariantResolvers,
  transcriptResolvers,
  transcriptFieldResolvers,
  variantResolvers,
])

const schema = makeExecutableSchema({
  typeDefs,
  resolvers,
})

module.exports = schema
