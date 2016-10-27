import express from 'express'
import { MongoClient } from 'mongodb'

const app = express()
let db

MongoClient.connect(process.env.MONGO_URL, (error, database) => {
  if (error) throw error
  db = database
  app.listen(8080, () => console.log('Listening on 8080'))
})

app.get('/data/variants', (request, response) => {
  db.collection('variants')
    .find({ genes: 'ENSG00000169174' })
    .toArray((error, variants) => {
      if (error) throw error
      response.json(variants)
    })
})
