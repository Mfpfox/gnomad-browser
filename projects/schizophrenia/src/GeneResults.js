/* eslint-disable react/prop-types */
import React, { PureComponent } from 'react'
import gql from 'graphql-tag'
import { graphql, compose } from 'react-apollo'
import styled from 'styled-components'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { List, Record } from 'immutable'

import { Table } from '@broad/table'

import {
  screenSize,
  Loading,
  GenePage,
  Summary,
  GeneSymbol,
  Search,
} from '@broad/ui'


function isEmpty(val) {
  return (
    val === undefined
    || val === null
    || val === ''
  )
}

const ResultsSearchWrapper = styled.div`
  margin-bottom: 10px;
  margin-top: 10px;
`

const schizophreniaGeneResultsQuery = gql`
  {
    schzGeneResults {
      gene_name
      description
      gene_id
      case_lof
      ctrl_lof
      pval_lof
      case_mpc
      ctrl_mpc
      pval_mpc
      pval_meta
    }
  }
`

const GeneResult = Record({
  gene_name: '',
  description: null,
  gene_id: null,
  case_lof: null,
  ctrl_lof: null,
  pval_lof: null,
  case_mpc: null,
  ctrl_mpc: null,
  pval_mpc: null,
  pval_meta: null,
})

const withQuery = graphql(schizophreniaGeneResultsQuery)

const tableConfig = (onHeaderClick, width) => {
  const mediumSize = (width < 900)
  return ({
    fields: [
      { dataKey: 'gene_name', title: 'Gene Name', dataType: 'link', onHeaderClick, width: 80, searchable: true },
      { dataKey: 'description', title: 'Description', dataType: 'string', onHeaderClick, width: 140, disappear: mediumSize },
      { dataKey: 'gene_id', title: 'Gene ID', dataType: 'string', onHeaderClick, width: 120, disappear: mediumSize },
      { dataKey: 'case_lof', title: 'Case LOF', dataType: 'integer', onHeaderClick, width: 60 },
      { dataKey: 'ctrl_lof', title: 'Ctrl LOF', dataType: 'integer', onHeaderClick, width: 60 },
      { dataKey: 'pval_lof', title: 'P-Val LOF', dataType: 'exponential', onHeaderClick, width: 80 },
      { dataKey: 'case_mpc', title: 'Case MPC', dataType: 'integer', onHeaderClick, width: 60, disappear: mediumSize },
      { dataKey: 'ctrl_mpc', title: 'Ctrl MPC', dataType: 'integer', onHeaderClick, width: 60, disappear: mediumSize },
      { dataKey: 'pval_mpc', title: 'P-Val MPC', dataType: 'exponential', onHeaderClick, width: 80 },
      { dataKey: 'pval_meta', title: 'P-Val Meta', dataType: 'exponential', onHeaderClick, width: 80 },
    ],
  })
}

class SchizophreniaGeneResults extends PureComponent {
  state = {
    searchText: '',
    sortKey: 'pval_meta',
    sortAscending: true,
  }

  setSearchText = searchText => this.setState({
    searchText: String(searchText).toUpperCase(),
  })

  setSortState = (sortKey) => {
    this.setState({
      sortKey,
      sortAscending: !this.state.sortAscending
    })
  }

  sortData = (data, key, ascending) => {
    if (data.isEmpty()) {
      return new List()
    }

    const comparator = (typeof data.first().get(key) === 'string')
      ? (a, b) => a.localeCompare(b)
      : (a, b) => a - b

    const sorter = ascending
      ? comparator
      : (a, b) => comparator(b, a)

    return data.sort((resultA, resultB) => {
      const sortValA = resultA.get(key)
      const sortValB = resultB.get(key)

      if (isEmpty(sortValA)) {
        return 1
      }

      if (isEmpty(sortValB)) {
        return -1
      }

      return sorter(sortValA, sortValB)
    })
  }

  geneOnClick = geneName => this.props.history.push(`/gene/${geneName}`)

  render () {
    const {
      data: { loading, schzGeneResults },
      screenSize,
    } = this.props

    if (loading) {
      return <Loading><h1>Loading</h1></Loading>
    }

    const tableWidth = (screenSize.width * 0.8) + 40
    const data = new List(schzGeneResults.map(e => new GeneResult(e)))
    const searchResults = data.filter((e) => {
      if (e.gene_name) {
        return e.gene_name.includes(this.state.searchText)
      }
      return false
    })
    const sortedData = this.sortData(searchResults, this.state.sortKey, this.state.sortAscending)

    return (
      <GenePage>
        <GeneSymbol>Exome meta-analysis results</GeneSymbol>
        <ResultsSearchWrapper>
          <Search
            placeholder={'Search genes'}
            onChange={this.setSearchText}
          />
        </ResultsSearchWrapper>
        {sortedData.isEmpty() ? 'No results found' : (
          <Table
            height={800}
            width={tableWidth}
            tableConfig={tableConfig(this.setSortState, screenSize.width)}
            tableData={sortedData}
            remoteRowCount={sortedData.size}
            loadMoreRows={() => {}}
            overscan={5}
            onRowClick={this.geneOnClick}
            onRowHover={() => {}}
            onScroll={() => {}}
            searchText={this.state.searchText}
            filteredIdList={new List(['test'])}
          />
        )}
      </GenePage>
    )
  }
}

const mapStatesToProps = state => ({
  screenSize: screenSize(state),
})

export default compose(
  withRouter,
  connect(mapStatesToProps),
  withQuery
)(SchizophreniaGeneResults)
