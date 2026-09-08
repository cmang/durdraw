{
  description = "Durdraw: ASCII, Unicode and ANSI art editor";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    { nixpkgs, self, ... }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
      python = pkgs.python3;
      pythonPackages = python.pkgs;
      projectData = builtins.fromTOML (builtins.readFile ./pyproject.toml);
    in
    {
      packages.${system}.default = pythonPackages.buildPythonApplication {
        pname = projectData.project.name;
        version = projectData.project.version;
        src = ./.;
        pyproject = true;
        nativeBuildInputs = [
          pythonPackages.setuptools
          pythonPackages.wheel
        ];
        buildInputs = [
          pkgs.fastfetch
          pkgs.ansilove
        ];
        doCheck = false;
      };

      devShells.${system}.default = pkgs.mkShell {
        buildInputs = [
          python
          pythonPackages.pip
          pythonPackages.setuptools
          pythonPackages.wheel
          pythonPackages.pytest
          pkgs.fastfetch
          pkgs.ansilove
          self.packages.${system}.default
        ];
      };
    };
}
