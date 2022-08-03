import axios from 'axios';
import {Server} from "./type";

export async function setServer(server: Server): Promise<Server> {
    console.log(JSON.stringify(server));
    const response = await axios.post('http://localhost:8002/api/server', server);
    console.log(response.data);
    return response.data;
}

export async function getServer(): Promise<Server> {
    const response = await axios.get('http://localhost:8002/api/server');
    console.log(response.data);
    return response.data;
}


