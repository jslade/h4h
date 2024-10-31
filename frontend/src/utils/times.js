export function to_locale_string(ts) {
    try {
        return (new Date(ts)).toLocaleString();
    } catch {
        return ts;
    }
}
