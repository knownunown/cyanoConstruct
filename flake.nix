{
  inputs = {
    nixpkgs.url = "nixpkgs";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, utils }: utils.lib.eachDefaultSystem
    (system:
      let pkgs = import nixpkgs { inherit system; };
          linuxPkgs = if pkgs.stdenv.isLinux then [ pkgs.python-language-server ] else [];
      in {
        devShell = pkgs.mkShell {
          name = "cc-devshell";

          # development dependencies
          buildInputs = with pkgs; [
            # backend
            python3 python3Packages.pylint poetry mypy black
          ] ++ (with nodePackages; [
            # frontend
            nodejs npm typescript-language-server vls
          ]) ++ linuxPkgs;

          nativeBuildInputs = with pkgs; [];
        };
      });
}
