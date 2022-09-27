import {ResourceField} from "../resource/type";
import {Server} from "../server/type";

export enum Operators {
    eq = "eq",
    ne = "ne",
    gt = "gt",
    lt = "lt",
    ge = "ge",
    le = "le",
    sa = "sa",
    eb = "eb",
    in = "in",
    not_in = "not_in",
    contains = "contains"
}

export interface FieldParameter {
    field: ResourceField;
    operator: Operators;
    value: string | number | string[] | number[] | boolean;
}

export interface IncludeParameter {
    resource: string;
    search_param: string;
    target?: string;
    reverse?: boolean;
    iterate?: boolean;
}

export interface ReverseChainParameter {
    resource: string;
    reference_param: string;
    search_param: string;
    operator: Operators;
    value: string | number | string[] | number[] | boolean;
}

export interface QueryParameters {
    resource: string;
    resource_parameters?: FieldParameter[];
    include_parameters?: IncludeParameter[];
    has_parameters?: ReverseChainParameter[];
}

export interface ResourceResults {
    resource: string;
    results: Object[];
}

export interface QueryInfo {
    server: Server;
    query_parameters: QueryParameters;
    start_time?: Date;
    query_string?: string;
    end_time?: Date;
}
export interface QueryResponse {
    query: QueryInfo;
    results: ResourceResults[];
}

