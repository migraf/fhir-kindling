export interface ServerCredentials {
    username?: string;
    password?: string;
    token?: string;
}

export interface Server {
    name?: string;
    api_url: string;
    credentials?: ServerCredentials;
}
