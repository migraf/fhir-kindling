import {FieldParameter} from "./type";

export function urlResourceField(field: FieldParameter): string {
    let operator = field.operator.valueOf();
    if (operator === "eq" || operator === "in") {
        return `${field.field.name}=${field.value}`;
    }
    if (operator === "ne" || operator === "not_in") {
        return `${field.field.name}=ne${field.value}`;
    }
    if (operator === "contains") {
        return `${field.field.name}:contains=${field.value}`;
    }
    return `${field.field.name}=${operator}${field.value}`;
}
