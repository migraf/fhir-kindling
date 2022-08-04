export interface ResourceField{
    name: string;
    type: string;
    description?: string;
    title?: string;
}

export interface ResourceFields{
    resource: string;
    fields: ResourceField[];
}
