{
  inputs = {
    nixpkgs.url = "nixpkgs/release-20.09";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, utils }: utils.lib.eachDefaultSystem
    (system:
      let pkgs = import nixpkgs { inherit system; };
      in {
        devShell = pkgs.mkShell {
          name = "cc-devshell";

          buildInputs = with pkgs; [
            python3 poetry
          ];

          nativeBuildInputs = with pkgs; [];
        };
      });
}
