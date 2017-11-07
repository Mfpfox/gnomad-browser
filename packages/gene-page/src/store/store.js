/* eslint-disable space-before-function-paren */
/* eslint-disable no-shadow */
/* eslint-disable comma-dangle */
/* eslint-disable import/no-unresolved */
/* eslint-disable import/extensions */

import {
  applyMiddleware,
  compose,
  combineReducers,
  createStore,
} from 'redux'

import thunk from 'redux-thunk'
import throttle from 'redux-throttle'
import createDebounce from 'redux-debounced'
import { createLogger } from 'redux-logger'
import { reduxSearch, reducer as searchReducer } from 'redux-search'

import createGeneReducer from '../resources/genes'
import createRegionReducer from '../resources/regions'

import createVariantReducer, {
  visibleVariantsById,
  filteredVariantsById,
  allVariantsInCurrentDataset,
} from '../resources/variants'

import { help } from '@broad/help'

import createActiveReducer from '../resources/active'

const logger = createLogger()

const defaultWait = 500
const defaultThrottleOption = { // https://lodash.com/docs#throttle
  leading: true,
  trailing: false,
}
const reduxThrottle = throttle(defaultWait, defaultThrottleOption)  // eslint-disable-line

const middlewares = [createDebounce(), thunk]

export default function createGenePageStore(appSettings, appReducers) {
  if (appSettings.logger) {
    middlewares.push(logger)
  }
  const rootReducer = combineReducers({
    active: createActiveReducer(appSettings),
    genes: createGeneReducer(appSettings),
    search: searchReducer,
    variants: createVariantReducer(appSettings),
    regions: createRegionReducer(appSettings),
    help,
    ...appReducers,
  })

  const finalCreateStore = compose(
    applyMiddleware(...middlewares),
    reduxSearch({
      resourceIndexes: {
        variants: appSettings.searchIndexes,
      },
      resourceSelector: appSettings.searchResourceSelector,
    }),
  )(createStore)

  return finalCreateStore(rootReducer)
}
