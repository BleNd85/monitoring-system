import axios from 'axios';

const client = axios.create({
     baseURL: '/collector/api/v1',
     timeout: 5000
})

const request = async (promise) => {
     try {
          const response = await promise
          return response.data
     }
     catch (error) {
          console.error('API error:', error)
          throw error.response?.data || error.messages
     }
}

export const getAgents = async () => {
     return request(client.get('/agents'))
}

export const registerAgent = async (data) => {
     return request(client.post('/agents', data))
}

export const deleteAgent = async (agentId) => {
     return request(client.delete(`/agents/${agentId}`))
}

export const getLatestMetrics = async (agentId) => {
     return request(client.get(`/metrics/${agentId}/latest`))
}

export const getRangeMetrics = async (agentId, start, end) => {
     return request(client.get(`/metrics/${agentId}/range`, {
          params: {
               start: start.toISOString(),
               end: end.toISOString(),
          }
     })
     )
}