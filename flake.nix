{
  inputs = {
    nixpkgs.url = "nixpkgs/release-21.05";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, utils }: utils.lib.eachDefaultSystem
    (system:
      let pkgs = import nixpkgs { inherit system; };
          linuxPkgs = if pkgs.stdenv.isLinux then [ /* pkgs.python-language-server */ ] else [];
      in {
        devShell = pkgs.mkShell {
          name = "cc-devshell";

          # development dependencies
          buildInputs = with pkgs; [
            # utilities
            sqlite

            # backend
            python3 python3Packages.pylint pyright poetry black
          ] ++ (with nodePackages; [
            # frontend
            nodejs npm typescript-language-server vls
          ]) ++ linuxPkgs;

          nativeBuildInputs = with pkgs; [];
        };
      });
}
