/* S, M, L, T
   S = Start / Promoter
   M = Middle
   L = Last (element before terminator)
   T = Terminator

   Components with equivalent PositionInfo will have equivalent spacers, by virtue of the
   CyanoConstruct system design.
*/
export enum PositionType {
    Promoter = "S",
    Middle = "M",
    Last = "L",
    Terminator = "T"
}

export interface PositionInfo {
    posType: PositionType,
    pos: number
}

// Usually 4 nucleotides in length.
export interface Spacers {
    left: String,
    right: String
}

export interface Fragment {
    name: string,
    'type': string,
    position: PositionInfo,
    spacers: Spacers,
}

export class PlaceholderFragment {
    name: string = "Placeholder";
    placeholder: boolean = true;
    position: PositionInfo = {
        posType: PositionType.Promoter,
        pos: 0,
    }
}

export type FragmentInfo = PlaceholderFragment | Fragment;

/*
export let PlaceholderFragment = {
    name: "placeholder",
    'type': 'N/A',
    position: {},
    spacers: {},
    placeholder: true,
};*/
