import uuid

class ParameterRegistry:
    def __init__(self):
        self.parameters: list[dict] = []
        self._ids_by_name: dict[str, str] = {}

    def get_or_create(self, name: str, slug: str, param_type: str, section_id: str) -> str:
        if name not in self._ids_by_name:
            param_id = str(uuid.uuid4())
            self._ids_by_name[name] = param_id
            self.parameters.append({
                "id": param_id,
                "name": name,
                "slug": slug,
                "type": param_type,
                "sectionId": section_id
            })
        return self._ids_by_name[name]
def make_dimension_tag(tag_name: str, display_name: str, field_id: int, widget_type: str) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "name": tag_name,
        "display-name": display_name,
        "type": "dimension",
        "dimension":["field", field_id, None],
        "widget-type": widget_type
    }