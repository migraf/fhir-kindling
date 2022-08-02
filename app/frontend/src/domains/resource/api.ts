import axios from 'axios';

export async function getResourceNames(): Promise<string[]> {
    const response = await axios.get('http://localhost:8002/api/resources');
    console.log(response.data);
    return response.data;
}

export async function getResourceFields(resourceName: string): Promise<string[]> {
    const response = await axios.get(`http://localhost:8002/api/resources/${resourceName}/fields`);
    console.log(response.data);
    return response.data;
}
