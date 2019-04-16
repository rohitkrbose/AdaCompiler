with Ada.Text_IO;
use Ada.Text_IO;

procedure While_L is
	procedure main is
		Count,k,Temperature : integer;
		z : float;
	begin
		Count := 1;
		z := 1;
		while z <= 5 loop
			Count := Count + 1;
			print_int (Count);
			z := z + 1;
		end loop;
		print_float (z);
		k := 7;
	end;
begin
	main;
end;