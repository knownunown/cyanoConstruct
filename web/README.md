# cyanoConstruct web

## Setup

### Import data from the prod database

```sh
sqlite3 -json prod.db \
'select SpacerData.terminalLetter, SpacerData.position, SpacerData.spacerLeft, SpacerData.spacerRight, NamedSequence.name, NamedSequence.elemType from Component
    INNER JOIN namedSequence ON Component.namedSequence_id = NamedSequence.id
    INNER JOIN SpacerData ON Component.spacerData_id = SpacerData.id' 
    | jq '[.[] | {name: .name, type: .elemType, pos: {posType: .terminalLetter, pos: .position}, spacers: {left: .spacerLeft, right: .spacerRight}}]'
```

Should return JSON suitable for input to the CC component.

## TODO: prod bundle, build, ...
