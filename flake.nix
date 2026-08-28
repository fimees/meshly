{
  description = "Meshly development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];

      forAllSystems = function:
        nixpkgs.lib.genAttrs systems (
          system:
            function nixpkgs.legacyPackages.${system}
        );
    in
    {
      devShells = forAllSystems (pkgs: {
        default = pkgs.mkShell {
          packages = with pkgs; [
            python3
            openssl
          ];

          shellHook = ''
            echo ""
            echo "  M E S H L Y"
            echo "  Development environment"
            echo ""
          '';
        };
      });
    };
}
