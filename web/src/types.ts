/* S, M, L, T
   S = Start / Promoter
   M = Middle
   L = Last (element before terminator)
   T = Terminator

   Components with equivalent PositionInfo will have equivalent spacers, by virtue of the
   CyanoConstruct system design.
*/

export interface PositionInfo {
    posType: PositionType;
    pos: number;
}

export enum PositionType {
    Promoter = "S",
    Middle = "M",
    Last = "L",
    Terminator = "T",
}

// Usually 4 nucleotides in length.
export interface Spacers {
    left: String,
    right: String,
}
