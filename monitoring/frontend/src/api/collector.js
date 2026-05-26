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

export const getAgents = () => request(client.get('/agents'))

export const registerAgent = (data) => request(client.post('/agents', data))

export const deleteAgentById = (agentId) => request(client.delete(`/agents/${agentId}`))


export const getLatestMetricsByAgentId = (agentId) => request(client.get(`/metrics/${agentId}/latest`))

export const getRangeMetricsByAgentId = (agentId, start, end) =>
     request(client.get(`/metrics/${agentId}/range`, {
          params: {
               start: start.toISOString(),
               end: end.toISOString(),
          }
     }))
