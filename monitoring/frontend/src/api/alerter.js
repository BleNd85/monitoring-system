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

export const getIncidents = async (limit = 100) => {
    return request(client.get('/incidents', {
        params: {
            limit
        }
    }))
}