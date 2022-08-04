import axios from 'axios';
import {ResourceFields} from "./type";

export async function getResourceNames(): Promise<string[]> {
    const response = await axios.get('http://localhost:8002/api/resources');
    console.log(response.data);
    return response.data;
}

export async function getResourceFields(resourceName: string): Promise<ResourceFields> {
    const response = await axios.get(`http://localhost:8002/api/resources/${resourceName}/fields`);
    console.log(response.data);
    return response.data;
}
