export interface ServerCredentials {
    username?: string;
    password?: string;
    token?: string;
}

export interface Server {
    name?: string;
    apiUrl: string;
    credentials?: ServerCredentials;
}
