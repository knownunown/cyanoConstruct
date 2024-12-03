{
  inputs = {
    nixpkgs.url = "nixpkgs/nixos-unstable";
    utils.url = "github:numtide/flake-utils";
    pyproject-nix.url = "github:nix-community/pyproject.nix";
    pyproject-nix.inputs.nixpkgs.follows = "nixpkgs";
    uv2nix.url = "github:adisbladis/uv2nix";
    uv2nix.inputs.pyproject-nix.follows = "pyproject-nix";
    uv2nix.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, utils, ... } @ inputs: utils.lib.eachDefaultSystem
    (system:
      let pkgs = import nixpkgs { inherit system; };
          # pkgsAMD64 = import nixpkgs { system = "x86_64-linux"; };
          lib = pkgs.lib;
          linuxPkgs = if pkgs.stdenv.isLinux then [ /* pkgs.python-language-server */ ] else [];
	        workspace = inputs.uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };
	        overlay = workspace.mkPyprojectOverlay {
            # Prefer prebuilt binary wheels as a package source.
            # Sdists are less likely to "just work" because of the metadata missing from uv.lock.
            # Binary wheels are more likely to, but may still require overrides for library dependencies.
	          sourcePreference = "wheel"; # or sourcePreference = "sdist";
          };

	        pyprojectOverrides = _final: _prev: {
            # Implement build fixups here.
          };

	        pythonSet =
            # Use base package set from pyproject.nix builders
            (pkgs.callPackage inputs.pyproject-nix.build.packages {
              python = pkgs.python3;
            }).overrideScope
              (lib.composeExtensions overlay pyprojectOverrides);
	        venv = pythonSet.mkVirtualEnv "cc-env" workspace.deps.default;

	    /*python = pkgs.python3.override {
	    self = pkgs.python3;
	    packageOverrides = overlay;
	  };*/ 
      in {
        devShell = pkgs.mkShell {
          name = "cc-devshell";

          # development dependencies
          buildInputs = with pkgs; [
            # poetryEnv
	          podman
	          uv
	          flyctl
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
	      # app = python.pkgs.cyanoconstruct;
	      packages = {
	        inherit venv;
	        docker = pkgs.dockerTools.buildLayeredImage {
	          name = "cyanoconstruct";
	          tag = "latest";
	          # architecture = "amd64";
	          config = {
	            Cmd = [
	              "${venv}/bin/gunicorn"
	              "--workers"
	              "1"
	              "--bind"
	              "0.0.0.0:8080"
	              "cyanoconstruct:app"
	            ];
	          };
	        };
	      };
      });
}
