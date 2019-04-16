with Ada.Text_IO;
use Ada.Text_IO;

procedure demo is
	function xyz (tem: array (1 .. 3) of integer) return integer is
		a : integer;
	begin
		a := tem( 1 );
		a := 5;
		print_int (a);
		return a;
	end; 
	procedure main is
		squares: array (1 .. 3) of integer;
		i : integer;
	begin
		i := 1;
		squares ( i ) := 1;
		-- squares ( i ) := squares(i) * 2;
		print_int( squares(i) );
		i := xyz(squares);
	end;
begin
	main;
end;