import axios from 'axios';

export async function getResourceNames(): Promise<string[]> {
    const response = await axios.get('http://localhost:8002/api/resources');
    console.log(response.data);
    return response.data;
}
