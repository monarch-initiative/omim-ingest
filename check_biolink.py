from importlib.resources import files
from linkml_runtime.utils.schemaview import SchemaView

# Load from installed package
biolink_yaml = files('biolink_model.schema') / 'biolink_model.yaml'
sv = SchemaView(str(biolink_yaml))

# Look up key predicates in detail
print("=" * 80)
print("KEY PREDICATES FOR GENE-DISEASE ASSOCIATIONS")
print("=" * 80)

for predicate in ["causes", "contributes_to", "gene_associated_with_condition", "predisposes_to_condition"]:
    slot = sv.get_slot(predicate)
    if slot:
        print(f"\n{predicate}:")
        print(f"  Description: {slot.description}")
        if hasattr(slot, 'exact_mappings') and slot.exact_mappings:
            print(f"  Exact mappings: {slot.exact_mappings}")
        if hasattr(slot, 'related_mappings') and slot.related_mappings:
            print(f"  Related mappings: {slot.related_mappings}")

# Check what the predicate constraints are for each association class
print("\n" + "=" * 80)
print("ASSOCIATION CLASSES AND THEIR PREDICATE CONSTRAINTS")
print("=" * 80)

for cls_name in ["causal gene to disease association", "correlated gene to disease association"]:
    cls = sv.get_class(cls_name)
    if cls:
        print(f"\n{cls_name}:")
        if cls.is_a:
            print(f"  Parent class: {cls.is_a}")
        
        # Get induced slots to see predicate range
        induced_slots = sv.class_induced_slots(cls_name)
        for islot in induced_slots:
            if islot.name == 'predicate':
                print(f"  Predicate slot:")
                if hasattr(islot, 'subproperty_of'):
                    print(f"    subproperty_of: {islot.subproperty_of}")
                if hasattr(islot, 'range'):
                    print(f"    range: {islot.range}")

