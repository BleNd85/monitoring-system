import axios from "axios";

const client = axios.create({
    baseURL: '/alerter/api/v1',
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

export const getIncidents = async (limit = 100) =>
    request(client.get('/incidents', { params: { limit } }))

export const getIncidentByAgentId = async (agent_id, limit = 50) =>
    request(client.get(`/incidents/${agent_id}`, { params: { limit } }))

export const resolveIncidentById = async (id) =>
    request(client.patch(`/incidents/${id}/resolve`), {})
