import React from 'react'

import { ExternalLink, List, ListItem } from '@gnomad/ui'

import MitochondrialVariantDetailPropType from './MitochondrialVariantDetailPropType'

const MitochondrialVariantReferenceList = ({ variant }) => {
  const { pos, ref, alt } = variant
  /* eslint-disable-next-line prettier/prettier */
  const ucscURL = `https://genome.ucsc.edu/cgi-bin/hgTracks?db=hg38&highlight=hg38.chrM%3A${pos}-${pos + (ref.length - 1)}&position=chrM%3A${pos - 25}-${pos + (ref.length - 1) + 25}`

  const mitomapURL = `https://mitomap.org/cgi-bin/search_allele?variant=${encodeURIComponent(
    `${pos}${ref}>${alt}`
  )}`

  return (
    <List>
      <ListItem>
        <ExternalLink href={ucscURL}>UCSC</ExternalLink>
      </ListItem>
      <ListItem>
        <ExternalLink href={mitomapURL}>Mitomap</ExternalLink>
      </ListItem>
    </List>
  )
}

MitochondrialVariantReferenceList.propTypes = {
  variant: MitochondrialVariantDetailPropType.isRequired,
}

export default MitochondrialVariantReferenceList
