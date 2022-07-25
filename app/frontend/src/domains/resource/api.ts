import axios from 'axios';

export async function getResourceNames(): Promise<string[]> {
    const response = await axios.get('http://localhost:8001/resources');
    return response.data;
}
