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

          buildInputs = with pkgs; [
            python3 python3Packages.pylint poetry mypy black
          ] ++ linuxPkgs;

          nativeBuildInputs = with pkgs; [];
        };
      });
}
